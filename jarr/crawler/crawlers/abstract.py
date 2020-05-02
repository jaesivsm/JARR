import logging

from jarr.bootstrap import conf
from jarr.controllers import (ArticleController, FeedBuilderController,
                              FeedController)
from jarr.crawler.article_builders.classic import ClassicArticleBuilder
from jarr.crawler.lib.headers_handling import (extract_feed_info,
                                               prepare_headers)
from jarr.crawler.requests_utils import (response_calculated_etag_match,
                                         response_etag_match)
from jarr.lib.const import UNIX_START
from jarr.lib.enums import FeedType
from jarr.lib.utils import jarr_get, utc_now
from jarr.metrics import FEED_FETCH as FETCH, FEED_LATENESS as LATENESS

logger = logging.getLogger(__name__)


class AbstractCrawler:
    feed_type = None  # type: FeedType
    article_builder = ClassicArticleBuilder

    def __init__(self, feed):
        self.feed = feed

    def _metric_fetch(self, result, level=logging.INFO):
        logger.log(level, 'feed responded with %s', result)
        FETCH.labels(feed_type=self.feed.feed_type.value, result=result).inc()

    def _metric_lateness(self, now):
        if not self.feed.last_retrieved \
                or self.feed.last_retrieved == UNIX_START:
            return
        delta = (self.feed.last_retrieved - now).total_seconds()
        LATENESS.labels(feed_type=self.feed.feed_type.value).observe(delta)

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
        now = utc_now()
        info = {'error_count': error_count, 'last_error': last_error,
                'user_id': self.feed.user_id, 'last_retrieved': now}
        self._metric_lateness(now)
        info.update(extract_feed_info({}))
        return FeedController().update({'id': self.feed.id}, info)

    def clean_feed(self, response, parsed_feed=None, **info):
        """Will reset the errors counters on a feed that have known errors"""
        now = utc_now()
        info.update(extract_feed_info(response.headers, response.text))
        info.update({'error_count': 0, 'last_error': None,
                     'last_retrieved': now})

        if parsed_feed is not None:  # updating feed with retrieved info
            fb_contr = FeedBuilderController(self.feed.link, parsed_feed)
            constructed = fb_contr.construct_from_xml_feed_content()
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
            self._metric_lateness(now)
            return FeedController(self.feed.user_id).update(
                    {'id': self.feed.id}, info)
        return None

    def parse_feed_response(self, response):
        raise NotImplementedError()

    def create_missing_article(self, response):
        logger.info('cache validation failed, challenging entries')
        parsed = self.parse_feed_response(response)
        if parsed is None:
            return

        ids, entries, skipped_list = [], {}, []
        for entry in parsed['entries']:
            if not entry:
                continue
            builder = self.article_builder(self.feed, entry)
            if builder.do_skip_creation:
                skipped_list.append(builder.entry_ids)
                logger.debug('skipping article')
                continue
            entry_ids = builder.entry_ids
            entries[tuple(sorted(entry_ids.items()))] = builder
            ids.append(entry_ids)
        if not ids and skipped_list:
            logger.debug('nothing to add (skipped %r) %r',
                         skipped_list, parsed)
            return
        logger.debug('found %d entries %r', len(ids), ids)

        article_created = False
        actrl = ArticleController(self.feed.user_id)
        new_entries_ids = list(actrl.challenge(ids=ids))
        logger.debug("%d entries wern't matched and will be created",
                    len(new_entries_ids))
        for id_to_create in new_entries_ids:
            article_created = True
            builder = entries[tuple(sorted(id_to_create.items()))]
            new_article = builder.enhance()
            logger.info('creating %r for %r - %r', new_article.get('title'),
                        new_article.get('user_id'), id_to_create)
            actrl.create(**new_article)

        if not article_created:
            logger.info('all article matched in db, adding nothing')

    def get_url(self):
        return self.feed.link

    def request(self):
        return jarr_get(self.get_url(),
                        timeout=conf.crawler.timeout,
                        user_agent=conf.crawler.user_agent,
                        headers=prepare_headers(self.feed))

    def is_cache_hit(self, response):
        if response.status_code == 304:
            self._metric_fetch('304', logging.DEBUG)
            return True
        if response.status_code == 226:
            self._metric_fetch('226')
            return False
        if response_etag_match(self.feed, response):
            self._metric_fetch('manual-hash-match', logging.DEBUG)
            return True
        if response_calculated_etag_match(self.feed, response):
            self._metric_fetch('home-made-hash-match', logging.DEBUG)
            return True
        self._metric_fetch('cache-miss')
        return False

    def crawl(self):
        logger.debug('%r - crawling resources', self.feed)
        try:
            response = self.request()
            response.raise_for_status()
        except Exception as error:
            self.set_feed_error(error=error)
            return

        if not self.is_cache_hit(response):
            self.create_missing_article(response)
