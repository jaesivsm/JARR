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

    def extract_lang(self, entry):
        return entry.get('language') or self._top_level.get('language')

    @staticmethod
    def extract_comments(entry):
        return entry.get('url') or entry.get('external_url')

    def _all_articles(self):
        known_links = {self.article['link'],
                       self.extract_link(self.entry),
                       self.article['comments']}
        yield self.article
        for i, link in enumerate(self.entry.get('attachments') or []):
            try:
                content_type = link['mime_type']
                title = link.get('title')
                link = link['url']
            except (KeyError, TypeError):
                continue
            if link in known_links:
                continue
            known_links.add(link)
            enclosure = self.template_article()
            enclosure['order_in_cluster'] = i
            for key, value in self.article.items():
                if key in {'title', 'lang', 'link_hash', 'entry_id'}:
                    enclosure[key] = value
            enclosure['link'] = link
            if title:
                enclosure['title'] = title
            self._feed_content_type(content_type, enclosure)
            yield enclosure
