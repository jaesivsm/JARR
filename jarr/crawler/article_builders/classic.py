import html
import json
import logging
from datetime import timezone

import dateutil.parser
from jarr.crawler.article_builders.abstract import AbstractArticleBuilder
from jarr.lib.utils import digest

logger = logging.getLogger(__name__)


class ClassicArticleBuilder(AbstractArticleBuilder):

    @staticmethod
    def extract_id(entry):
        if entry.get('entry_id'):
            return entry['entry_id']
        if entry.get('id'):
            return entry['id']
        if entry.get('link'):
            # entry_id is part of an index, limiting size here
            return digest(entry['link'], alg='sha1')
        return digest(json.dumps(entry, sort_keys=True), alg='sha1')

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

    def extract_lang(self, entry):
        lang = None
        if entry.get('content', []):
            lang = (entry['content'][0] or {}).get('language')
        if not lang:
            for sub_key in 'title_detail', 'summary_detail':
                lang = entry.get(sub_key, {}).get('language')
                if lang:
                    break
        if not lang:
            return self._top_level.get('language')
        return lang

    @staticmethod
    def extract_comments(entry):
        return entry.get('comments')

    def _all_articles(self):
        known_links = {self.article['link'],
                       self.extract_link(self.entry),
                       self.article['comments']}
        yield self.article
        for i, link in enumerate(self.entry.get('links') or []):
            try:
                if link['rel'] != 'enclosure':
                    continue
                content_type = link['type']
                link = link['href']
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
            self._feed_content_type(content_type, enclosure)
            yield enclosure
