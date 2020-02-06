import html
import logging
from datetime import timezone
from urllib.parse import SplitResult, urlsplit, urlunsplit

import dateutil.parser
from requests.exceptions import MissingSchema

from jarr.lib.filter import process_filters, FiltersAction
from jarr.lib.html_parsing import extract_tags, extract_title, extract_lang
from jarr.lib.utils import jarr_get, utc_now
from jarr.lib.article_cleaner import clean_urls

logger = logging.getLogger(__name__)
PROCESSED_DATE_KEYS = {'published', 'created', 'updated'}
FETCHABLE_DETAILS = {'link', 'title', 'tags', 'lang'}


def extract_id(entry):
    """ extract a value from an entry that will identify it among the other of
    that feed"""
    return entry.get('entry_id') or entry.get('id') or entry['link']


def construct_article(entry, feed, user_agent,
                      fields=None, fetch=True, resolv=False):
    "Safe method to transorm a feedparser entry into an article"
    now = utc_now()
    article = {}

    def push_in_article(key, *args):
        """feeding article with entry[key]
        if 'fields' is None or if key in 'fields'.
        You can either pass on value or a callable and some args to feed it"""
        if fields and key not in fields:
            return
        if len(args) == 1:
            value = args[0]
        else:
            value = args[0](*args[1:])
        article[key] = value
    push_in_article('feed_id', feed.id)
    push_in_article('user_id', feed.user_id)
    push_in_article('entry_id', extract_id, entry)
    push_in_article('retrieved_date', now)
    if not fields or 'date' in fields:
        for date_key in PROCESSED_DATE_KEYS:
            if entry.get(date_key):
                try:
                    article['date'] = dateutil.parser.parse(entry[date_key])\
                            .astimezone(timezone.utc)
                except Exception:
                    pass
                else:
                    break
    push_in_article('content', get_entry_content, entry)
    push_in_article('comments', entry.get, 'comments')
    push_in_article('lang', get_entry_lang, entry)
    if fields is None or FETCHABLE_DETAILS.intersection(fields):
        details = get_article_details(entry, user_agent,
                                      fetch=fetch, resolv=resolv)
        for detail, value in details.items():
            if not article.get(detail):
                push_in_article(detail, value)
        if details.get('tags') and article.get('tags'):
            push_in_article('tags',
                            set(details['tags']).union, article['tags'])
        if 'content' in article and details.get('link'):
            push_in_article('content',
                            clean_urls, article['content'], details['link'])
    return article


def get_entry_content(entry):
    content = ''
    if entry.get('content'):
        content = entry['content'][0]['value']
    elif entry.get('summary'):
        content = entry['summary']
    return content


def get_entry_lang(entry):
    lang = None
    if entry.get('content', []):
        lang = (entry['content'][0] or {}).get('language')
        if lang:
            return lang
    for sub_key in 'title_detail', 'summary_detail':
        lang = entry.get(sub_key, {}).get('language')
        if lang:
            return lang
    return lang


def _fetch_article(link, user_agent):
    try:
        # resolves URL behind proxies (like feedproxy.google.com)
        return jarr_get(link, timeout=5, user_agent=user_agent)
    except MissingSchema:
        split = urlsplit(link)
        for scheme in 'https', 'http':
            new_link = urlunsplit(SplitResult(scheme, *split[1:]))
            try:
                return jarr_get(new_link, timeout=5, user_agent=user_agent)
            except Exception as error:
                continue
    except Exception as error:
        logger.info("Unable to get the real URL of %s. Won't fix "
                    "link or title. Error: %s", link, error)


def get_article_details(entry, user_agent, fetch=True, resolv=False):
    detail = {'title': html.unescape(entry.get('title', '')),
              'link': entry.get('link'),
              'tags': {tag.get('term', '').lower().strip()
                       for tag in entry.get('tags', [])
                       if tag.get('term', '').strip()}}
    missing_elm = any(not detail.get(key) for key in ('title', 'tags', 'lang'))
    if fetch and detail['link'] and (resolv or missing_elm):
        response = _fetch_article(detail['link'], user_agent)
        if response is None:
            return detail
        detail['link'] = response.url
        if not detail['title']:
            detail['title'] = extract_title(response)
        detail['tags'] = detail['tags'].union(extract_tags(response))
        lang = extract_lang(response)
        if lang:
            detail['lang'] = lang
    return detail


def get_skip_and_ids(entry, feed, user_agent, resolv=False):
    entry_ids = construct_article(entry, feed, user_agent,
                {'entry_id', 'feed_id', 'user_id'}, fetch=False, resolv=resolv)
    skipped, _, _ = process_filters(feed.filters,
            construct_article(entry, feed, user_agent, {'title', 'tags'},
                              fetch=False, resolv=resolv),
            {FiltersAction.SKIP})
    return skipped, entry_ids
