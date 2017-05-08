import re
from bs4 import BeautifulSoup
from lib.integrations.abstract import AbstractIntegration

KOREUS_FEED = re.compile(r'^https?://feeds.feedburner.com/Koreus-articles$')


class KoreusIntegration(AbstractIntegration):

    def match_entry_parsing(self, feed, entry):
        if not len(entry.get('summary_detail', [])):
            return False
        return bool(entry['summary_detail'].get('value')
                    and KOREUS_FEED.match(feed.get('link', '')))

    def entry_parsing(self, feed, entry):
        summary_detail = BeautifulSoup(entry['summary_detail']['value'],
                                       'html.parser')
        link = summary_detail.find_all('a')[0]
        entry['comments'] = entry['link']
        entry['link'] = link.attrs['href']
        return True
