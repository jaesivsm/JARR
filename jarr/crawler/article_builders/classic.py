import html
import json
import logging
from datetime import timezone
from hashlib import sha1
from urllib.parse import SplitResult, urlsplit, urlunsplit

import dateutil.parser
from requests.exceptions import MissingSchema

from jarr.lib.filter import FiltersAction, process_filters
from jarr.lib.html_parsing import extract_lang, extract_tags, extract_title
from jarr.lib.utils import utc_now
from jarr.utils import jarr_get

logger = logging.getLogger(__name__)


class ClassicArticleBuilder:

    def __init__(self, feed, entry):
        self.feed = feed
        self.entry = entry
        self.article = {}
        self.construct(self.entry)

    @property
    def entry_ids(self):
        return {k: self.article[k] for k in {'entry_id', 'feed_id', 'user_id'}}

    @property
    def do_skip_creation(self):
        return process_filters(self.feed.filters, self.article,
                               FiltersAction.SKIP)[0]

    def template_article(self):
        return {'feed_id': self.feed.id,
                'category_id': self.feed.category_id,
                'user_id': self.feed.user_id,
                'retrived_date': utc_now()}

    @staticmethod
    def extract_id(entry):
        if entry.get('entry_id'):
            return entry['entry_id']
        if entry.get('id'):
            return entry['id']
        if entry.get('link'):
            # entry_id is part of an index, limiting size here
            return sha1(entry['link'].encode('utf8')).hexdigest()
        return sha1(json.dumps(entry,
                               sort_keys=True).encode('utf8')).hexdigest()

    @staticmethod
    def extract_date(entry):
        for date_key in 'published', 'created', 'updated':
            if entry.get(date_key):
                try:
                    return dateutil.parser.parse(entry[date_key])\
                            .astimezone(timezone.utc)
                except Exception:
                    pass

    @staticmethod
    def extract_title(entry):
        return html.unescape(entry.get('title', ''))

    @staticmethod
    def extract_tags(entry):
        return {tag.get('term', '').lower().strip()
                for tag in entry.get('tags', [])
                if tag.get('term', '').strip()}

    @staticmethod
    def extract_link(entry):
        return entry.get('link')

    @staticmethod
    def extract_content(entry):
        if entry.get('content'):
            return entry['content'][0]['value']
        if entry.get('summary'):
            return entry['summary']
        return ''

    @staticmethod
    def extract_lang(entry):
        lang = None
        if entry.get('content', []):
            lang = (entry['content'][0] or {}).get('language')
        if not lang:
            for sub_key in 'title_detail', 'summary_detail':
                lang = entry.get(sub_key, {}).get('language')
                if lang:
                    break
        return lang

    @staticmethod
    def extract_comments(entry):
        return entry.get('comments')

    def construct(self, entry):
        self.article = self.template_article()
        if not entry:
            return
        self.article['entry_id'] = self.extract_id(entry)
        self.article['date'] = self.extract_date(entry)
        self.article['title'] = self.extract_title(entry)
        self.article['tags'] = self.extract_tags(entry)
        self.article['link'] = self.extract_link(entry)
        self.article['content'] = self.extract_content(entry)
        self.article['lang'] = self.extract_lang(entry)
        self.article['comments'] = self.extract_comments(entry)

    @staticmethod
    def _fetch_article(link):
        try:
            # resolves URL behind proxies (like feedproxy.google.com)
            return jarr_get(link)
        except MissingSchema:
            split = urlsplit(link)
            for scheme in 'https', 'http':
                new_link = urlunsplit(SplitResult(scheme, *split[1:]))
                try:
                    return jarr_get(new_link)
                except Exception as error:
                    continue
        except Exception as error:
            logger.info("Unable to get the real URL of %s. Won't fix "
                        "link or title. Error: %s", link, error)

    def enhance(self):
        page = self._fetch_article(self.article['link'])
        if not page:
            return self.article
        self.article['link'] = page.url
        if not self.article.get('title'):
            self.article['title'] = extract_title(page)
        self.article['tags'] = self.article['tags'].union(extract_tags(page))
        lang = extract_lang(page)
        if lang:
            self.article['lang'] = lang
        return self.article