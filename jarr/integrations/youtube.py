import re
from blinker import signal

CHANNEL_RE = re.compile(r'^https?://www.youtube.com/channel/')
FEED_URL = 'https://www.youtube.com/feeds/videos.xml?channel_id='
feed_creation = signal('feed_creation')


@feed_creation.connect
def youtube_integration(sender, feed, **kwargs):
    has_link, site_link = bool(feed.get('link')), feed.get('site_link', '')
    if has_link or not CHANNEL_RE.match(site_link):
        return

    feed['link'] = FEED_URL + CHANNEL_RE.split(site_link, 1)[1]
