import logging

import requests
from requests.exceptions import MissingSchema

from jarr.bootstrap import conf
from jarr.lib.filter import FiltersAction, process_filters
from jarr.lib.enums import ArticleType
from jarr.lib.utils import utc_now

logger = logging.getLogger(__name__)


class AbstractArticleBuilder:

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
                               {FiltersAction.SKIP})['skipped']

    def template_article(self):
        return {'feed_id': self.feed.id,
                'category_id': self.feed.category_id,
                'user_id': self.feed.user_id,
                'retrieved_date': utc_now()}

    @staticmethod
    def extract_id(entry):
        raise NotImplementedError()

    @staticmethod
    def extract_date(entry):
        raise NotImplementedError()

    @staticmethod
    def extract_title(entry):
        raise NotImplementedError()

    @staticmethod
    def extract_tags(entry):
        raise NotImplementedError()

    @staticmethod
    def extract_link(entry):
        raise NotImplementedError()

    @staticmethod
    def extract_content(entry):
        raise NotImplementedError()

    @staticmethod
    def extract_lang(entry):
        raise NotImplementedError()

    @staticmethod
    def extract_comments(entry):
        raise NotImplementedError()

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

    @classmethod
    def _head(cls, url):
        try:
            headers = {'User-Agent': conf.crawler.user_agent}
            head = requests.head(url, headers=headers, allow_redirects=True,
                                 timeout=conf.crawler.timeout)
            head.raise_for_status()
            return head
        except MissingSchema:
            for scheme in 'https://', 'https:', 'http://', 'http:':
                try:
                    return cls._head(scheme + url)
                except Exception as error:
                    logger.debug('got %r for url %s%s', error, scheme, url)
                    continue

    def enhance(self):
        head = self._head(self.article['link'])
        if head:
            self.article['link'] = head.url
            if head.headers['Content-Type'].startswith('image/'):
                self.article['article_type'] = ArticleType.image
            elif head.headers['Content-Type'].startswith('video/'):
                self.article['article_type'] = ArticleType.video
        return self.article
