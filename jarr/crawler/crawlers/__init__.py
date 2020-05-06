"""Root package for all implemented Crawlers."""
from .abstract import AbstractCrawler
from .classic import ClassicCrawler
from .json import JSONCrawler
from .koreus import KoreusCrawler
from .reddit import RedditCrawler
from .rss_bridge import InstagramCrawler, SoundcloudCrawler
from .tumblr import TumblrCrawler

__all__ = ['AbstractCrawler', 'ClassicCrawler', 'InstagramCrawler',
           'SoundcloudCrawler', 'KoreusCrawler', 'RedditCrawler',
           'JSONCrawler', 'TumblrCrawler']
