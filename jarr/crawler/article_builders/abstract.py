import logging

import requests
from requests.exceptions import MissingSchema

from jarr.bootstrap import conf
from jarr.lib.content_generator import is_embedded_link
from jarr.lib.enums import ArticleType
from jarr.lib.filter import FiltersAction, process_filters
from jarr.lib.utils import utc_now
from jarr.lib.article_cleaner import get_goose
from jarr.utils import jarr_get

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
        try:
            self.article['date'] = self.extract_date(entry)
        except Exception:
            self.article['date'] = utc_now()
        self.article['title'] = self.extract_title(entry)
        self.article['tags'] = self.extract_tags(entry)
        self.article['link'] = self.extract_link(entry)
        self.article['content'] = self.extract_content(entry)
        self.article['lang'] = self.extract_lang(entry)
        self.article['comments'] = self.extract_comments(entry)

    @classmethod
    def _head(cls, url, reraise=False):
        try:
            headers = {'User-Agent': conf.crawler.user_agent}
            head = requests.head(url, headers=headers, allow_redirects=True,
                                 timeout=conf.crawler.timeout)
            head.raise_for_status()
            return head
        except MissingSchema:
            if reraise:
                raise
            for scheme in 'https:', 'https://', 'http:', 'http://':
                try:
                    return cls._head(scheme + url, reraise=True)
                except Exception as error:
                    logger.debug('got %r for url %s%s', error, scheme, url)
                    continue
        except Exception:
            logger.error("couldn't fetch %r", url)

    def enhance(self, fetch_page=True):
        if self.feed.truncated_content:
            return self.article  # will be retrieved on clustering

        head = self._head(self.article['link'])
        if not head:
            return self.article

        self.article['link'] = head.url  # correcting link in case of redirect
        content_type = str(head.headers.get('Content-Type')) or ''
        if content_type.startswith('image/'):
            fetch_page = False
            self.article['article_type'] = ArticleType.image
        elif content_type.startswith('video/'):
            fetch_page = False
            self.article['article_type'] = ArticleType.video
        elif is_embedded_link(self.article['link']):
            self.article['article_type'] = ArticleType.embedded
        if fetch_page:
            _, extract = get_goose(self.article['link'])
            for key in 'link', 'title', 'lang':
                if not self.article.get(key) and extract.get(key):
                    self.article[key] = extract[key]
            self.article['tags'] = self.article['tags'].union(extract['tags'])
        elif not self.article.get('lang') \
                and head.headers.get('Content-Language'):
            # correcting lang from http headers
            lang = head.headers['Content-Language'].split(',')[0]
            self.article['lang'] = lang
        return self.article
