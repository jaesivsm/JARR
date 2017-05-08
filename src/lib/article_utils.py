import html
import logging
import re
from datetime import timezone
from enum import Enum
from urllib.parse import SplitResult, urlsplit, urlunsplit

import dateutil.parser
from requests.exceptions import MissingSchema

from bootstrap import conf
from lib.html_parsing import extract_tags, extract_title
from lib.utils import jarr_get, utc_now
from web.lib.article_cleaner import clean_urls

logger = logging.getLogger(__name__)
PROCESSED_DATE_KEYS = {'published', 'created', 'updated'}


def extract_id(entry):
    """ extract a value from an entry that will identify it among the other of
    that feed"""
    return entry.get('entry_id') or entry.get('id') or entry['link']


def construct_article(entry, feed, fields=None, fetch=True):
    "Safe method to transorm a feedparser entry into an article"
    now = utc_now()
    article = {}

    def push_in_article(key, value):
        """feeding article with entry[key]
        if 'fields' is None or if key in 'fields'"""
        if not fields or key in fields:
            article[key] = value
    push_in_article('feed_id', feed['id'])
    push_in_article('user_id', feed['user_id'])
    push_in_article('entry_id', extract_id(entry))
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
    push_in_article('content', get_article_content(entry))
    push_in_article('comments', entry.get('comments'))
    if fields is None or {'link', 'title', 'tags'}.intersection(fields):
        link, title, tags = get_article_details(
                article.get('link') or entry.get('link'), entry, fetch)
        push_in_article('link', link)
        push_in_article('title', title)
        push_in_article('tags', tags)
        if 'content' in article:
            push_in_article('content', clean_urls(article['content'], link))
    return article


def get_article_content(entry):
    content = ''
    if entry.get('content'):
        content = entry['content'][0]['value']
    elif entry.get('summary'):
        content = entry['summary']
    return content


def _fetch_article(link):
    try:
        # resolves URL behind proxies (like feedproxy.google.com)
        return jarr_get(link, timeout=5)
    except MissingSchema:
        split = urlsplit(link)
        for scheme in 'https', 'http':
            new_link = urlunsplit(SplitResult(scheme, *split[1:]))
            try:
                return jarr_get(new_link, timeout=5)
            except Exception as error:
                continue
    except Exception as error:
        logger.info("Unable to get the real URL of %s. Won't fix "
                    "link or title. Error: %s", link, error)


def get_article_details(article_link, entry, fetch=True):
    article_title = html.unescape(entry.get('title', ''))
    tags = {tag.get('term', '').lower().strip()
            for tag in entry.get('tags', [])
            if tag.get('term', '').strip()}
    if fetch and conf.CRAWLER_RESOLV and article_link or not article_title:
        response = _fetch_article(article_link)
        if response is None:
            return article_link, article_title or 'No title', tags
        article_link = response.url
        if not article_title:
            article_title = extract_title(response, og_prop='og:title')
        tags = tags.union(extract_tags(response))
    return article_link, article_title or 'No title', tags


class FiltersAction(Enum):
    READ = 'mark as read'
    LIKED = 'mark as favorite'
    SKIP = 'skipped'


class FiltersType(Enum):
    REGEX = 'regex'
    MATCH = 'simple match'
    EXACT_MATCH = 'exact match'
    TAG_MATCH = 'tag match'
    TAG_CONTAINS = 'tag contains'


class FiltersTrigger(Enum):
    MATCH = 'match'
    NO_MATCH = 'no match'


def _is_filter_to_skip(filter_action, only_actions, article):
    if filter_action not in only_actions:
        return True
    if filter_action in {FiltersType.REGEX, FiltersType.MATCH,
            FiltersType.EXACT_MATCH} and 'title' not in article:
        return True
    if filter_action in {FiltersType.TAG_MATCH, FiltersType.TAG_CONTAINS} \
            and 'tags' not in article:
        return True
    return False


def _is_filter_matching(filter_, article):
    pattern = filter_.get('pattern', '')
    filter_type = FiltersType(filter_.get('type'))
    filter_trigger = FiltersTrigger(filter_.get('action on'))
    if filter_type is not FiltersType.REGEX:
        pattern = pattern.lower()
    title = article.get('title', '').lower()
    tags = [tag.lower() for tag in article.get('tags', [])]
    if filter_type is FiltersType.REGEX:
        match = re.match(pattern, title)
    elif filter_type is FiltersType.MATCH:
        match = pattern in title
    elif filter_type is FiltersType.EXACT_MATCH:
        match = pattern == title
    elif filter_type is FiltersType.TAG_MATCH:
        match = pattern in tags
    elif filter_type is FiltersType.TAG_CONTAINS:
        match = any(pattern in tag for tag in tags)
    return match and filter_trigger is FiltersTrigger.MATCH \
            or not match and filter_trigger is FiltersTrigger.NO_MATCH


def process_filters(filters, article, only_actions=None):
    skipped, read, liked = False, None, False
    filters = filters or []
    if only_actions is None:
        only_actions = set(FiltersAction)
    for filter_ in filters:
        filter_action = FiltersAction(filter_.get('action'))

        if _is_filter_to_skip(filter_action, only_actions, article):
            logger.debug('ignoring filter %r' % filter_)
            continue

        if not _is_filter_matching(filter_, article):
            continue

        if filter_action is FiltersAction.READ:
            read = True
        elif filter_action is FiltersAction.LIKED:
            liked = True
        elif filter_action is FiltersAction.SKIP:
            skipped = True

    if skipped or read or liked:
        logger.info("%r applied on %r", filter_action.value,
                    article.get('link') or article.get('title'))
    return skipped, read, liked


def get_skip_and_ids(entry, feed):
    entry_ids = construct_article(entry, feed,
                {'entry_id', 'feed_id', 'user_id'}, fetch=False)
    skipped, _, _ = process_filters(feed['filters'],
            construct_article(entry, feed, {'title', 'tags'}, fetch=False),
            {FiltersAction.SKIP})
    return skipped, entry_ids
