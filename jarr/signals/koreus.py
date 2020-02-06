import re
from bs4 import BeautifulSoup
from .base import entry_parsing

KOREUS_FEED = re.compile(r'^https?://feeds.feedburner.com/Koreus-articles$')


@entry_parsing.connect
def koreus_integration(sender, feed, entry, **kwargs):
    is_koreus_feed = bool(KOREUS_FEED.match(feed.link or ''))
    has_sufficient_data = bool(entry.get('summary_detail', {}).get('value'))
    if not is_koreus_feed or not has_sufficient_data:
        return

    summary_detail = BeautifulSoup(entry['summary_detail']['value'],
                                   'html.parser')
    link = summary_detail.find_all('a')[0]
    entry['comments'] = entry['link']
    entry['link'] = link.attrs['href']
    return
