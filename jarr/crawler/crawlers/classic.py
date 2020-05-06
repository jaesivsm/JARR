import logging

import feedparser

from jarr.controllers.feed_builder import FeedBuilderController
from jarr.crawler.crawlers.abstract import AbstractCrawler
from jarr.lib.enums import FeedType

logger = logging.getLogger(__name__)


class ClassicCrawler(AbstractCrawler):
    feed_type = FeedType.classic

    def parse_feed_response(self, response):
        parsed = feedparser.parse(response.content.strip())
        if not FeedBuilderController(self.feed.link, parsed).is_parsed_feed():
            self.set_feed_error(parsed_feed=parsed)
            return
        return parsed
