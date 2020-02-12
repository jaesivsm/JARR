import logging

from bs4 import BeautifulSoup

from jarr.crawler.crawlers.classic import ClassicCrawler
from jarr.crawler.article_builders.reddit import RedditArticleBuilder
from jarr.lib.jarr_types import FeedType

logger = logging.getLogger(__name__)


class RedditCrawler(ClassicCrawler):
    feed_type = FeedType.reddit
    article_builder = RedditArticleBuilder
