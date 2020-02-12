import logging

from bs4 import BeautifulSoup

from jarr.crawler.crawlers.classic import ClassicCrawler
from jarr.lib.jarr_types import FeedType

logger = logging.getLogger(__name__)


class RedditCrawler(ClassicCrawler):
    feed_type = FeedType.reddit

    @staticmethod
    def parse_entry(entry):
        has_sufficient_data = bool(len(entry.get('content', []))
                                and entry['content'][0].get('value'))
        if not has_sufficient_data:
            return entry

        content = BeautifulSoup(entry['content'][0]['value'], 'html.parser')
        try:
            link, comments = content.find_all('a')[-2:]
        except Exception:
            logger.warning('failed to parse %r', entry)
            return entry
        entry['tags'] = []  # reddit tags are irrelevant, removing them
        if link.text != '[link]' or comments.text != '[comments]':
            return entry
        entry['link'] = link.attrs['href']
        entry['comments'] = comments.attrs['href']
        if entry['link'] == entry['comments']:
            del entry['comments']
        return entry
