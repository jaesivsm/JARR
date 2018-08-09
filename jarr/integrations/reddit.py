import re
import logging
from blinker import signal
from bs4 import BeautifulSoup


REDDIT_FEED = re.compile(r'^https?://www.reddit.com/r/\S+/.rss$')
logger = logging.getLogger(__name__)
feed_creation, entry_parsing = signal('feed_creation'), signal('entry_parsing')


@feed_creation.connect
def reddit_integration_feed_creation(sender, feed):
    feed['integration_reddit'] = bool(REDDIT_FEED.match(feed.get('link', '')))


@entry_parsing.connect
def reddit_integration_entry_parsing(sender, feed, entry):
    is_reddit_feed = bool(feed.get('integration_reddit')
                          and REDDIT_FEED.match(feed.get('link', '')))
    has_sufficient_data = bool(len(entry.get('content', []))
                               and entry['content'][0].get('value'))
    if not is_reddit_feed or not has_sufficient_data:
        return

    content = BeautifulSoup(entry['content'][0]['value'], 'html.parser')
    try:
        link, comments = content.find_all('a')[-2:]
    except Exception:
        logger.warning('failed to parse %r', entry)
        return
    entry['tags'] = []  # reddit tags are irrelevant, removing them
    if link.text != '[link]' or comments.text != '[comments]':
        return
    entry['link'] = link.attrs['href']
    entry['comments'] = comments.attrs['href']
    if entry['link'] == entry['comments']:
        del entry['comments']
    return
