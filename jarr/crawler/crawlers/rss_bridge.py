from urllib.parse import SplitResult, urlencode, urlsplit, urlunsplit

from jarr.bootstrap import conf
from jarr.crawler.article_builders.rss_bridge import (
    RSSBridgeArticleBuilder, RSSBridgeTwitterArticleBuilder)
from jarr.crawler.crawlers.classic import ClassicCrawler
from jarr.lib.enums import FeedType


class RssBridgeAbstractCrawler(ClassicCrawler):
    bridge = None  # type: str
    bridge_format = 'AtomFormat'
    article_builder = RSSBridgeArticleBuilder
    feed_type = None  # forcing this crawler to be ignored

    def get_url(self):
        split = urlsplit(conf.plugins.rss_bridge) \
                if conf.plugins.rss_bridge else None

        query = {'action': 'display', 'format': self.bridge_format,
                 'bridge': self.bridge, 'u': self.feed.link}

        return urlunsplit(SplitResult(scheme=split.scheme, netloc=split.netloc,
                                      path=split.path or '/',
                                      query=urlencode(query), fragment=''))


class InstagramCrawler(RssBridgeAbstractCrawler):
    feed_type = FeedType.instagram
    bridge = 'InstagramBridge'


class SoundcloudCrawler(RssBridgeAbstractCrawler):
    feed_type = FeedType.soundcloud
    bridge = 'SoundcloudBridge'


class TwitterCrawler(RssBridgeAbstractCrawler):
    feed_type = FeedType.twitter
    bridge = 'TwitterBridge'
    article_builder = RSSBridgeTwitterArticleBuilder
