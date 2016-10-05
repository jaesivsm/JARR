import html
import logging
import dateutil.parser
from datetime import datetime, timezone
from bs4 import BeautifulSoup, SoupStrainer

from bootstrap import conf
from lib.utils import jarr_get
from web.lib.article_cleaner import clean_urls

logger = logging.getLogger(__name__)


def extract_id(entry):
    """ extract a value from an entry that will identify it among the other of
    that feed"""
    return entry.get('entry_id') or entry.get('id') or entry['link']


def construct_article(entry, feed):
    "Safe method to transorm a feedparser entry into an article"
    now = datetime.utcnow()
    date = None
    for date_key in ('published', 'created', 'date'):
        if entry.get(date_key):
            try:
                date = dateutil.parser.parse(entry[date_key])\
                        .astimezone(timezone.utc)
            except Exception:
                pass
            else:
                break

    content = get_article_content(entry)
    link, title = get_article_details(entry)
    content = clean_urls(content, link)

    return {'feed_id': feed['id'],
            'user_id': feed['user_id'],
            'entry_id': extract_id(entry),
            'link': link, 'content': content, 'title': title,
            'retrieved_date': now, 'date': date or now}


def get_article_content(entry):
    content = ''
    if entry.get('content'):
        content = entry['content'][0]['value']
    elif entry.get('summary'):
        content = entry['summary']
    return content


def get_article_details(entry):
    article_link = entry.get('link')
    article_title = html.unescape(entry.get('title', ''))
    if conf.CRAWLER_RESOLV and article_link or not article_title:
        try:
            # resolves URL behind proxies (like feedproxy.google.com)
            response = jarr_get(article_link)
        except Exception as error:
            logger.warning("Unable to get the real URL of %s. Won't fix link "
                           "or title. Error: %s", article_link, error)
            return article_link, article_title or 'No title'
        article_link = response.url
        if not article_title:
            bs_parsed = BeautifulSoup(response.content, 'html.parser',
                                      parse_only=SoupStrainer('head'))
            try:
                article_title = bs_parsed.find_all('title')[0].text
            except IndexError:  # no title
                pass
    return article_link, article_title or 'No title'
