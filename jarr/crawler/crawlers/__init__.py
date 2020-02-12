from .abstract import AbstractCrawler
from .classic import ClassicCrawler
from .koreus import KoreusCrawler
from .reddit import RedditCrawler
from .rss_bridge import InstagramCrawler, SoundcloudCrawler


def get_crawler(feed_type):
    if feed_type is ClassicCrawler.feed_type:
        return ClassicCrawler
    for crawler in ClassicCrawler.__subclasses__():
        if feed_type is crawler.feed_type:
            return crawler
    raise ValueError('No crawler for %r' % feed_type)


__all__ = ['AbstractCrawler', 'ClassicCrawler', 'InstagramCrawler',
           'SoundcloudCrawler', 'KoreusCrawler', 'RedditCrawler']
