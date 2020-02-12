from bs4 import BeautifulSoup

from jarr.crawler.crawlers.classic import ClassicCrawler
from jarr.lib.jarr_types import FeedType


class KoreusCrawler(ClassicCrawler):
    feed_type = FeedType.koreus

    @staticmethod
    def parse_entry(entry):
        has_sufficient_data = entry.get('summary_detail', {}).get('value')
        if not has_sufficient_data:
            return entry

        summary_detail = BeautifulSoup(entry['summary_detail']['value'],
                                       'html.parser')
        link = summary_detail.find_all('a')[0]
        entry['comments'] = entry['link']
        entry['link'] = link.attrs['href']
        return entry
