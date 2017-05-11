import re
from bs4 import BeautifulSoup
from lib.integrations.abstract import AbstractIntegration

REDDIT_FEED = re.compile(r'^https?://www.reddit.com/r/\S+/.rss$')


class RedditIntegration(AbstractIntegration):

    def match_feed_creation(self, feed):
        return bool(REDDIT_FEED.match(feed.get('link', '')))

    def feed_creation(self, feed):
        feed['integration_reddit'] = True
        return True

    def match_entry_parsing(self, feed, entry):
        if not len(entry.get('content', [])):
            return False
        return bool(feed.get('integration_reddit')
                    and entry['content'][0].get('value')
                    and REDDIT_FEED.match(feed.get('link', '')))

    def entry_parsing(self, feed, entry):
        content = BeautifulSoup(entry['content'][0]['value'], 'html.parser')
        link, comments = content.find_all('a')[-2:]
        entry['tags'] = []  # reddit tags are irrelevant, removing them
        if link.text != '[link]' or comments.text != '[comments]':
            return False
        entry['link'] = link.attrs['href']
        entry['comments'] = comments.attrs['href']
        if entry['link'] == entry['comments']:
            del entry['comments']
        return True
