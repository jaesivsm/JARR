import html
import json
import logging
from datetime import timezone
from hashlib import sha1

import dateutil.parser

from jarr.crawler.article_builders.abstract import AbstractArticleBuilder

logger = logging.getLogger(__name__)


class ClassicArticleBuilder(AbstractArticleBuilder):

    def __init__(self, feed, entry):
        super.__init__(feed, entry)
        self._links = set()

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
                    logger.error("Couldn't parse %r", entry[date_key])

    @staticmethod
    def extract_title(entry):
        return html.unescape(entry.get('title', ''))

    @staticmethod
    def extract_tags(entry):
        return {tag.get('term', '').lower().strip()
                for tag in entry.get('tags', [])
                if tag.get('term', '').strip()}

    def extract_link(self, entry):
        link = entry.get('link')
        self._links.add(link)
        return link

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

    def _head(self, url, reraise=False):
        head = super()._head(url, reraise=False)
        if head is not None:
            self._links.add(head.url)
        return head

    def _all_articles(self):
        yield self.article
        if not self.article.get('link_hash'):
            # ensuring link_hash, to ensure clustering on link_hash
            self.article['link_hash'] = self.to_hash(clean_head.url)
        for link in (self.entry.get('links') or []):
            if link.get('href') in self._links:
                continue
            article = {key: value for key, value in self.articles.items()
                       if key in {'title', 'lang', 'link_hash', 'entry_id'}}
            self._feed_content_type(link.get('type'), article)
            yield article
