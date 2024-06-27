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

    @classmethod
    def _reach_in_parseditem(cls, entry, key: str, sub_key: str):
        value = entry.get(key)
        if isinstance(value, str):
            yield value
        elif isinstance(value, list):
            for sub_value in value:
                if isinstance(sub_value, dict):
                    if sub_value.get(sub_key):
                        yield sub_value[sub_key]
        elif isinstance(value, dict):
            if value.get(sub_key):
                yield value[sub_key]

    @classmethod
    def extract_title(cls, entry, max_length=100):
        for key in "title", "title_detail", "content":
            for value in cls._reach_in_parseditem(entry, key, "value"):
                return html.unescape(value[:max_length])

    @staticmethod
    def extract_tags(entry):
        return {tag["term"].lower().strip()
                for tag in entry.get("tags", [])
                if (tag.get("term") or '').strip()}

    @classmethod
    def extract_link(cls, entry):
        for key in "link", "links":
            for value in cls._reach_in_parseditem(entry, key, "href"):
                yield value

    @classmethod
    def extract_content(cls, entry):
        for key in "summary", "summary_detail", "content":
            for value in cls._reach_in_parseditem(entry, key, "value"):
                return value
        return ""

    def extract_lang(self, entry):
        for key in "summary_detail", "content", "title_detail":
            for value in self._reach_in_parseditem(entry, key, "language"):
                return value
        return self._top_level.get("language")

    @staticmethod
    def extract_comments(entry):
        return entry.get('comments')

    def _all_articles(self):
        known_links = {self.article['link'],
                       self.extract_link(self.entry),
                       self.article['comments']}
        yield self.article
        count = 0
        for enclosure_type in "links", "media_content":
            for enclosure in (self.entry.get(enclosure_type) or []):
                cluster_member = self.template_article()
                try:
                    content_type = enclosure["type"]
                    if (
                        enclosure_type == "links"
                        and enclosure.get("rel") == "enclosure"
                    ):
                        cluster_member["link"] = enclosure["href"]
                    elif enclosure_type == "media_content":
                        cluster_member["link"] = enclosure["url"]
                except (KeyError, TypeError):
                    continue
                # Not adding cluster member twice
                if cluster_member["link"] in known_links:
                    continue
                known_links.add(cluster_member["link"])
                # Not adding cluster memeber without type
                self._feed_content_type(content_type, cluster_member)
                if not cluster_member.get("article_type"):
                    continue
                count += 1
                cluster_member["order_in_cluster"] = count
                for key, value in self.article.items():
                    if key in {"title", "lang", "link_hash", "entry_id"}:
                        cluster_member[key] = value
                yield cluster_member
