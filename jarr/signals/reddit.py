import re
from .base import feed_creation

REDDIT_FEED = re.compile(r'^https?://www.reddit.com/r/\S+/.rss$')


@feed_creation.connect
def reddit_integration(sender, feed):
    feed['integration_reddit'] = bool(REDDIT_FEED.match(feed.get('link', '')))
