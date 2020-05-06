from jarr.crawler.crawlers.classic import ClassicCrawler
from jarr.lib.enums import FeedType
from jarr.crawler.article_builders.koreus import KoreusArticleBuilder


class KoreusCrawler(ClassicCrawler):
    feed_type = FeedType.koreus
    article_builder = KoreusArticleBuilder
