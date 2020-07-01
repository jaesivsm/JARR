from urllib.parse import SplitResult, urlencode, urlsplit, urlunsplit

from jarr.bootstrap import conf
from jarr.crawler.crawlers.classic import ClassicCrawler
from jarr.lib.enums import FeedType
from jarr.crawler.article_builders.twitter import TwitterArticleBuilder


class RssBridgeMixin:
    bridge = None  # type: str
    bridge_format = 'AtomFormat'

    def get_url(self):
        split = urlsplit(conf.plugins.rss_bridge) \
                if conf.plugins.rss_bridge else None

        query = {'action': 'display', 'format': self.bridge_format,
                 'bridge': self.bridge, 'u': self.feed.link}

        return urlunsplit(SplitResult(scheme=split.scheme,
                                      netloc=split.netloc,
                                      path=split.path or '/',
                                      query=urlencode(query), fragment=''))


class InstagramCrawler(RssBridgeMixin, ClassicCrawler):
    feed_type = FeedType.instagram
    bridge = 'InstagramBridge'


class SoundcloudCrawler(RssBridgeMixin, ClassicCrawler):
    feed_type = FeedType.soundcloud
    bridge = 'Soundcloud'


class TwitterCrawler(RssBridgeMixin, ClassicCrawler):
    feed_type = FeedType.twitter
    bridge = 'Twitter'
    article_builder = TwitterArticleBuilder
