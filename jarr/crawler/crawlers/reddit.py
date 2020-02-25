from jarr.crawler.crawlers.classic import ClassicCrawler
from jarr.crawler.article_builders.reddit import RedditArticleBuilder
from jarr.lib.jarr_types import FeedType


class RedditCrawler(ClassicCrawler):
    feed_type = FeedType.reddit
    article_builder = RedditArticleBuilder
