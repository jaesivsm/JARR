import logging

import feedparser

from jarr.bootstrap import conf
from jarr.controllers import ArticleController, FeedController
from jarr.crawler.article import construct_article, get_skip_and_ids
from jarr.crawler.lib.headers_handling import (extract_feed_info,
                                               prepare_headers)
from jarr.crawler.requests_utils import (response_calculated_etag_match,
                                         response_etag_match)
from jarr.lib import reasons
from jarr.lib.feed_utils import construct_feed_from, is_parsing_ok
from jarr.lib.utils import jarr_get, utc_now
from jarr.signals import entry_parsing

logger = logging.getLogger(__name__)


class ClassicCrawler:

    def __init__(self, feed):
        self.feed = feed

    def set_feed_error(self, error=None, parsed_feed=None):
        error_count = self.feed.error_count + 1
        if error:
            last_error = str(error)
        elif parsed_feed:
            last_error = str(parsed_feed.get('bozo_exception', ''))
        if self.feed.error_count > conf.feed.error_threshold:
            level = logging.WARNING
        else:
            level = logging.DEBUG
        logger.log(level, 'an error occured while fetching feed; '
                'bumping error count to %r', error_count)
        logger.debug("last error details %r", last_error)
        info = {'error_count': error_count, 'last_error': last_error,
                'user_id': self.feed.user_id, 'last_retrieved': utc_now()}
        info.update(extract_feed_info({}))
        return FeedController().update({'id': self.feed.id}, info)

    def clean_feed(self, response, parsed_feed=None, **info):
        """Will reset the errors counters on a feed that have known errors"""
        info.update(extract_feed_info(response.headers, response.text))
        info.update({'error_count': 0, 'last_error': None,
                    'last_retrieved': utc_now()})

        if parsed_feed is not None:  # updating feed with retrieved info
            constructed = construct_feed_from(self.feed.link, parsed_feed, self.feed,
                    timeout=conf.crawler.timeout,
                    user_agent=conf.crawler.user_agent)
            for key in 'description', 'site_link', 'icon_url':
                if constructed.get(key):
                    info[key] = constructed[key]

        info = {key: value for key, value in info.items()
                if getattr(self.feed, key) != value}

        # updating link on permanent move /redirect
        if response.history and self.feed.link != response.url and any(
                resp.status_code in {301, 308} for resp in response.history):
            logger.warning('feed moved from %r to %r',
                           self.feed.link, response.url)
            info['link'] = response.url

        if info:
            return FeedController(self.feed.user_id).update(
                    {'id': self.feed.id}, info)
        return None

    def create_missing_article(self, response, **kwargs):
        logger.info('cache validation failed, challenging entries')
        parsed = feedparser.parse(response.content.strip())
        if is_parsing_ok(parsed):
            self.clean_feed(response, parsed, **kwargs)
        else:
            self.set_feed_error(parsed_feed=parsed)
            return

        ids, entries, skipped_list = [], {}, []
        for entry in parsed['entries']:
            if not entry:
                continue
            entry_parsing.send('crawler', feed=self.feed, entry=entry)
            skipped, entry_ids = get_skip_and_ids(entry, self.feed,
                    user_agent=conf.crawler.user_agent,
                    resolv=conf.crawler.resolv)
            if skipped:
                skipped_list.append(entry_ids)
                logger.debug('skipping article')
                continue
            entries[tuple(sorted(entry_ids.items()))] = entry
            ids.append(entry_ids)
        if not ids and skipped_list:
            logger.debug('nothing to add (skipped %r) %r', skipped_list, parsed)
            return
        logger.debug('found %d entries %r', len(ids), ids)

        article_created = False
        actrl = ArticleController(self.feed.user_id)
        new_entries_ids = list(actrl.challenge(ids=ids))
        logger.debug("%d entries wern't matched and will be created",
                    len(new_entries_ids))
        for id_to_create in new_entries_ids:
            article_created = True
            new_article = construct_article(
                    entries[tuple(sorted(id_to_create.items()))], self.feed,
                    user_agent=conf.crawler.user_agent,
                    resolv=conf.crawler.resolv)
            logger.info('creating %r for %r - %r', new_article.get('title'),
                        new_article.get('user_id'), id_to_create)
            actrl.create(**new_article)

        if not article_created:
            logger.info('all article matched in db, adding nothing')

    def fetch(self):
        logger.debug('%r %r - fetching resources',
                     self.feed.id, self.feed.title)
        try:
            resp = jarr_get(self.feed.link,
                            timeout=conf.crawler.timeout,
                            user_agent=conf.crawler.user_agent,
                            headers=prepare_headers(self.feed))
            resp.raise_for_status()
        except Exception as error:
            self.set_feed_error(error=error)
            return

        # checking if cache was validated
        kwargs = {}
        if resp.status_code == 304:
            logger.info('feed responded with 304')
            self.clean_feed(resp,
                            cache_type=reasons.CacheReason.status_code_304)
        elif resp.status_code == 226:
            logger.info('feed responded with 226')
            kwargs['cache_support_a_im'] = True
        elif response_etag_match(self.feed, resp):
            self.clean_feed(resp, cache_type=reasons.CacheReason.etag)
        elif response_calculated_etag_match(self.feed, resp):
            self.clean_feed(resp,
                            cache_type=reasons.CacheReason.etag_calculated)
        else:
            logger.debug('etag mismatch %r != %r',
                         resp.headers.get('etag'), self.feed.etag)
            self.create_missing_article(resp, **kwargs)
