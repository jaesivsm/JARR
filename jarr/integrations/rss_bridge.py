import re
from urllib.parse import urlencode, urlsplit, urlunsplit, SplitResult
from blinker import signal
from jarr.bootstrap import conf

INSTA_REGEX = re.compile('^https?://(www.)?instagram.com/([^ \t\n\r\f\v/]+)')
feed_creation = signal('feed_creation')


@feed_creation.connect
def instagram_integration(sender, feed, **kwargs):
    try:
        u_ = INSTA_REGEX.split(feed.get('site_link', ''), 1)[2]
    except Exception:
        return False

    split = urlsplit(conf.plugins.rss_bridge) \
            if conf.plugins.rss_bridge else None

    query = {'action': 'display', 'format': 'AtomFormat',
             'bridge': 'InstagramBridge', 'u': u_}

    feed['link'] = urlunsplit(SplitResult(scheme=split.scheme,
                              netloc=split.netloc,
                              path=split.path or '/',
                              query=urlencode(query), fragment=''))
