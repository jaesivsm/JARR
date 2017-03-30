"""
Here's a sum up on how it works :

CrawlerScheduler.run
    will retreive a list of feeds to be refreshed and pass result to
CrawlerScheduler.callback
    which will retreive each feed and treat result with
FeedCrawler.callback
    which will interprete the result (status_code, etag) collect ids
    and match them agaisnt jarr which will cause
JarrUpdater.callback
    to create the missing entries
"""

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime, timedelta

import feedparser
from requests_futures.sessions import FuturesSession

from bootstrap import conf
from lib.article_utils import construct_article, get_skip_and_ids
from lib.feed_utils import construct_feed_from, is_parsing_ok
from lib.utils import default_handler, to_hash, utc_now
from crawler.lib import headers_handling

logger = logging.getLogger(__name__)
logging.captureWarnings(True)
FUTURES = []


class AbstractCrawler:
    pool = ThreadPoolExecutor(max_workers=conf.CRAWLER_NBWORKER)
    session = FuturesSession(executor=pool)

    def __init__(self, auth):
        self.auth = auth
        self.session.verify = False
        self.url = conf.PLATFORM_URL

    def query_jarr(self, method, urn, data=None):
        """A wrapper for internal call, method should be ones you can find
        on requests (header, post, get, options, ...), urn the distant
        resources you want to access on jarr, and data, the data you wanna
        transmit."""
        if data is None:
            data = {}
        method = getattr(self.session, method)
        future = method("%s%s/%s" % (self.url, conf.API_ROOT.strip('/'), urn),
                        auth=self.auth, timeout=conf.CRAWLER_TIMEOUT,
                        data=json.dumps(data, default=default_handler),
                        headers={'Content-Type': 'application/json',
                                 'User-Agent': conf.CRAWLER_USER_AGENT})
        FUTURES.append(future)
        return future

    def wait(self, max_wait=600, wait_for=2, checks=10):
        start, checked = datetime.now(), 0
        max_wait_delta = timedelta(seconds=max_wait)
        time.sleep(wait_for * 2)
        while True:
            time.sleep(wait_for)
            # checking not thread is still running
            # some thread are running and we are not behind
            if datetime.now() - start <= max_wait_delta \
                    and any(fu.running() for fu in FUTURES):
                # let's wait and see if it's not okay next time
                continue
            if checks > checked:
                checked += 1
                continue
            # all thread are done, let's exit
            if all(fu.done() for fu in FUTURES):
                break
            # some thread are still running and we're gonna future.wait on 'em
            wait_minus_passed = max_wait - (datetime.now() - start).seconds
            if wait_minus_passed > 0:
                max_wait = wait_minus_passed
            try:  # no idea why wait throw ValueError around
                wait(FUTURES, timeout=max_wait)
            except ValueError:
                logger.exception('something bad happened:')
            break


class AbstractFeedCrawler(AbstractCrawler):

    def __init__(self, feed, auth):
        self.feed = feed
        self.base_msg = '%r %r - ' % (self.feed['id'], self.feed['title'])
        super().__init__(auth)

    def log(self, level, message, *args, **kwargs):
        return getattr(logger, level)(self.base_msg + message, *args, **kwargs)


class JarrUpdater(AbstractFeedCrawler):

    def __init__(self, feed, entries, headers, auth):
        self.entries = entries
        self.headers = headers
        super().__init__(feed, auth)

    def callback(self, response):
        """Will process the result from the challenge, creating missing article
        and updating the feed"""
        article_created = False
        try:
            response = response.result()
            response.raise_for_status()
        except Exception:
            logger.exception('error while contacting JARR:')
            # ignore error on when contacting JARR
            # leave it to the next iteration
            return
        if response.status_code != 204:
            results = response.json()
            self.log('debug', "%d entries wern't matched and will be created",
                     len(results))
            entries = []
            for id_to_create in results:
                article_created = True
                entry = construct_article(
                        self.entries[tuple(sorted(id_to_create.items()))],
                        self.feed)
                self.log('info', 'creating %r for %r - %r', entry.get('title'),
                         entry.get('user_id'), id_to_create)
                entries.append(entry)
            self.query_jarr('post', 'articles', entries)

        if not article_created:
            self.log('info', 'all article matched in db, adding nothing')


class FeedCrawler(AbstractFeedCrawler):

    def clean_feed(self, response, parsed_feed=None):
        """Will reset the errors counters on a feed that have known errors"""
        info = headers_handling.extract_feed_info(response.headers)
        info.update({'error_count': 0, 'last_error': None,
                     'last_retrieved': utc_now()})

        if parsed_feed is not None:  # updating feed with retrieved info
            constructed = construct_feed_from(
                    self.feed['link'], parsed_feed, self.feed)
            for key in 'description', 'site_link', 'icon_url':
                if constructed.get(key):
                    info[key] = constructed[key]

        info = {key: value for key, value in info.items()
                if self.feed.get(key) != value}

        # updating link on permanent move /redirect
        if response.history and self.feed['link'] != response.url and any(
                resp.status_code in {301, 308} for resp in response.history):
            self.log('warn', 'feed moved from %r to %r',
                     self.feed['link'], response.url)
            info['link'] = response.url

        if info:
            self.query_jarr('put', 'feed/%d' % self.feed['id'], info)

    def set_feed_error(self, error=None, parsed_feed=None):
        error_count = self.feed['error_count'] + 1
        if error:
            last_error = str(error)
        elif parsed_feed:
            last_error = str(parsed_feed.get('bozo_exception', ''))
        if self.feed['error_count'] > conf.FEED_ERROR_THRESHOLD:
            self.log('warn', 'an error occured while fetching feed; '
                     'bumping error count to %r', error_count)
        info = {'error_count': error_count, 'last_error': last_error,
                'user_id': self.feed['user_id'], 'last_retrieved': utc_now()}
        info.update(headers_handling.extract_feed_info({}))
        future = self.query_jarr('put', 'feed/%d' % self.feed['id'], info)

    def response_match_cache(self, response):
        if 'etag' not in response.headers:
            self.log('debug', 'manually generating etag')
            response.headers['etag'] = 'jarr/"%s"' % to_hash(response.text)
        if response.headers['etag'] and self.feed['etag'] \
                and response.headers['etag'] == self.feed['etag']:
            if 'jarr' in self.feed['etag']:
                msg = "calculated hash matches (%d)"
            else:
                msg = "feed responded with same etag (%d)"
            self.log('info', msg, response.status_code)
            return True
        return False

    def callback(self, response):
        """will fetch the feed and interprete results (304, etag) or will
        challenge jarr to compare gotten entries with existing ones"""
        try:
            response = response.result()
            response.raise_for_status()
        except Exception as error:
            self.set_feed_error(error=error)
            return

        if response.status_code == 304:
            self.log('info', 'feed responded with 304')
            self.clean_feed(response)
            return
        if self.response_match_cache(response):
            self.clean_feed(response)
            return
        else:
            self.log('debug', 'etag mismatch %r != %r',
                     response.headers['etag'], self.feed['etag'])
        self.log('info', 'cache validation failed, challenging entries')

        parsed_response = feedparser.parse(response.content.strip())
        if is_parsing_ok(parsed_response):
            self.clean_feed(response)
        else:
            self.set_feed_error(parsed_feed=parsed_response)
            return

        ids, entries, skipped_list = [], {}, []
        for entry in parsed_response['entries']:
            if not entry:
                continue
            skipped, entry_ids = get_skip_and_ids(entry, self.feed)
            if skipped:
                skipped_list.append(entry_ids)
                self.log('debug', 'skipping article')
                continue
            entries[tuple(sorted(entry_ids.items()))] = entry
            ids.append(entry_ids)
        if not ids and skipped_list:
            self.log('debug', 'nothing to add (skipped %r) %r',
                     skipped_list, parsed_response)
            return
        self.log('debug', 'found %d entries %r', len(ids), ids)
        future = self.query_jarr('get', 'articles/challenge', {'ids': ids})
        updater = JarrUpdater(self.feed, entries, response.headers, self.auth)
        future.add_done_callback(updater.callback)


class CrawlerScheduler(AbstractCrawler):

    def __init__(self, username, password):
        self.auth = (username, password)
        super(CrawlerScheduler, self).__init__(self.auth)

    def callback(self, response):
        """processes feeds that need to be fetched"""
        try:
            response = response.result()
            response.raise_for_status()
        except Exception:
            logger.exception('Something went wrong when retrieving feeds:')
            return
        if response.status_code == 204:
            logger.debug("No feed to fetch")
            return
        feeds = response.json()
        logger.debug('%d to fetch %r', len(feeds), feeds)
        for feed in feeds:
            logger.debug('%r %r - fetching resources',
                         feed['id'], feed['title'])
            future = self.session.get(feed['link'],
                    timeout=conf.CRAWLER_TIMEOUT,
                    headers=headers_handling.prepare_headers(feed))
            FUTURES.append(future)

            feed_crwlr = FeedCrawler(feed, self.auth)
            future.add_done_callback(feed_crwlr.callback)

    def run(self, **kwargs):
        """entry point, will retreive feeds to be fetch
        and launch the whole thing"""
        logger.debug('retreving fetchable feed')
        future = self.query_jarr('get', 'feeds/fetchable', kwargs)
        future.add_done_callback(self.callback)
