import html
import logging
from datetime import timezone

import dateutil.parser

from jarr.crawler.article_builders.abstract import AbstractArticleBuilder
from jarr.lib.utils import utc_now

logger = logging.getLogger(__name__)


class JsonArticleBuilder(AbstractArticleBuilder):

    @staticmethod
    def extract_id(entry):
        return entry['id']

    @staticmethod
    def extract_date(entry):
        published = entry.get('date_published')
        if published:
            return dateutil.parser.parse(published).astimezone(timezone.utc)
        return utc_now()

    @staticmethod
    def extract_title(entry):
        if entry.get('title'):
            return html.unescape(entry['title'])

    @staticmethod
    def extract_tags(entry):
        return set(entry.get('tags') or [])

    @staticmethod
    def extract_link(entry):
        return entry.get('external_url') or entry.get('url')

    @staticmethod
    def extract_content(entry):
        for content_key in 'content_html', 'content_text':
            if entry.get(content_key):
                return entry[content_key]
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
        return entry.get('url') or entry.get('external_url')
