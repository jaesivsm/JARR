from .classic import ClassicCrawler
from .koreus import KoreusCrawler
from .reddit import RedditCrawler
from .rss_bridge import InstagramCrawler, SoundcloudCrawler


__all__ = ['ClassicCrawler', 'InstagramCrawler', 'SoundcloudCrawler',
           'KoreusCrawler', 'RedditCrawler']
