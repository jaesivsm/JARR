from jarr.crawler.crawlers.abstract import AbstractCrawler
from jarr.lib.enums import FeedType
from jarr.crawler.article_builders.json import JsonArticleBuilder


class JSONCrawler(AbstractCrawler):
    feed_type = FeedType.json
    article_builder = JsonArticleBuilder

    def parse_feed_response(self, response):
        parsed = response.json()
        parsed['entries'] = parsed.pop('items')
        return parsed
