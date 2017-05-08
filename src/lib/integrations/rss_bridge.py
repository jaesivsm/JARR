import re
from bootstrap import conf
from urllib.parse import urlencode, urlsplit, urlunsplit, SplitResult
from lib.integrations.abstract import AbstractIntegration


class RssBridgeAbstractIntegration(AbstractIntegration):
    bridge_type = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.split = urlsplit(conf.PLUGINS_RSS_BRIDGE) \
                if conf.PLUGINS_RSS_BRIDGE else None

    def get_u(self, feed):
        raise NotImplementedError()

    def match_feed_creation(self, feed):
        return bool(self.split and not feed.get('link') and self.get_u(feed))

    def feed_creation(self, feed):
        query = {'action': 'display', 'format': 'AtomFormat',
                 'bridge': self.bridge_type, 'u': self.get_u(feed)}

        feed['link'] = urlunsplit(SplitResult(scheme=self.split.scheme,
                                  netloc=self.split.netloc,
                                  path=self.split.path or '/',
                                  query=urlencode(query), fragment=''))
        return True


class RegexRssBridgeAbstractIntegration(RssBridgeAbstractIntegration):
    regex = None

    def get_u(self, feed):
        split = self.regex.split(feed.get('site_link', ''), 1)
        if len(split) > 1:
            return split[2]
        return False


class InstagramIntegration(RegexRssBridgeAbstractIntegration):
    regex = re.compile('^https?://(www.)?instagram.com/([^ \t\n\r\f\v/]+)')
    bridge_type = 'InstagramBridge'
