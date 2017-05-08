import re
from lib.integrations.abstract import AbstractIntegration

CHANNEL_RE = re.compile(r'^https?://www.youtube.com/channel/')
FEED_URL = 'https://www.youtube.com/feeds/videos.xml?channel_id='


class YoutubeIntegration(AbstractIntegration):

    def match_feed_creation(self, feed, **kwargs):
        no_link, site = not feed.get('link'), feed.get('site_link', '')
        return no_link and CHANNEL_RE.match(site)

    def feed_creation(self, feed, **kwargs):
        feed['link'] = FEED_URL + CHANNEL_RE.split(feed['site_link'], 1)[1]
        return True
