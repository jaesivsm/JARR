from jarr.crawler.crawlers.classic import ClassicCrawler
from jarr.crawler.article_builders.reddit import RedditArticleBuilder
from jarr.lib.enums import FeedType


class RedditCrawler(ClassicCrawler):
    feed_type = FeedType.reddit
    article_builder = RedditArticleBuilder
