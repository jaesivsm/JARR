import logging

import feedparser

from jarr.bootstrap import conf
from jarr.controllers.feed_builder import FeedBuilderController
from jarr.crawler.crawlers.abstract import AbstractCrawler
from jarr.crawler.lib.headers_handling import prepare_headers
from jarr.lib.jarr_types import FeedType
from jarr.lib.utils import jarr_get

logger = logging.getLogger(__name__)


class ClassicCrawler(AbstractCrawler):
    feed_type = FeedType.classic

    def parse_feed_response(self, response):
        parsed = feedparser.parse(response.content.strip())
        if not FeedBuilderController(self.feed.link, parsed).is_parsed_feed():
            self.set_feed_error(parsed_feed=parsed)
            return
        return parsed

    def request(self):
        return jarr_get(self.get_url(),
                        timeout=conf.crawler.timeout,
                        user_agent=conf.crawler.user_agent,
                        headers=prepare_headers(self.feed))
