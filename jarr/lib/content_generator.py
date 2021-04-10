import html
import logging
import re
from functools import lru_cache

from goose3 import Goose
from lxml import etree
import urllib.parse

from jarr.bootstrap import conf
from jarr.controllers.article import to_vector
from jarr.lib.enums import ArticleType, FeedType

logger = logging.getLogger(__name__)
IMG_ALT_MAX_LENGTH = 100
YOUTUBE_RE = re.compile(
        r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))'
        r'(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$')


def is_embedded_link(link):
    return YOUTUBE_RE.match(link)


class ContentGenerator:
    article_type = None
    feed_type = None

    def __init__(self, article):
        self.article = article
        self._page = None
        self.extracted_infos = {}

    def _get_goose(self):
        goose = Goose({"browser_user_agent": conf.crawler.user_agent})
        try:
            self._page = goose.extract(self.article.link)
        except Exception as error:
            logger.error("something wrong happened while trying to fetch "
                         "%r: %r", self.article.link, error)
        if not self._page:
            return False
        lang = self._page.opengraph.get('locale') or self._page.meta_lang
        self.extracted_infos['lang'] = lang
        self.extracted_infos['link'] = self._page.final_url
        keywords = set(self._page.meta_keywords.split(', '))
        self.extracted_infos['tags'] = set(self._page.tags).union(keywords)
        self.extracted_infos['title'] = self._page.title
        return True

    def get_vector(self):
        if self._page is None:
            self._get_goose()
        if self._page and self.extracted_infos:
            return to_vector(self.extracted_infos, self._page)

    def _from_goose_to_html(self, encoding="utf8"):
        result = ""
        current_node = self._page.top_node
        while True:
            result += etree.tostring(current_node,
                                     encoding=encoding).decode(encoding)
            current_node = current_node.getnext()
            if current_node is None:
                break
        return result

    @staticmethod
    def generate():
        return {}

    def generate_and_merge(self, cluster):
        article_content = self.generate()
        if not article_content:
            return False
        if not cluster.content:
            cluster.content = article_content
            return True
        cluster.content['multi'] = True
        if cluster.content['type'] == 'mixed':
            cluster.content['contents'].append(article_content)
        elif cluster.content['type'] == article_content['type']:
            cluster.content = {'type': 'mixed', 'multi': True,
                               'contents': [cluster.content,
                                            article_content]}


class EmbeddedContentGenerator(ContentGenerator):
    article_type = ArticleType.embedded

    def get_vector(self):
        return None

    def generate(self):
        yt_match = YOUTUBE_RE.match(self.article.link)
        if yt_match:
            logger.info('%r constructing embedded youtube content '
                        'from article', self.article)
            try:
                return {'type': self.article_type.value, 'player': 'youtube',
                        'videoId': yt_match.group(5)}
            except IndexError:
                pass
        else:
            logger.warning('embedded video not recognized %r',
                           self.article.link)
        return {}


class TruncatedContentGenerator(ContentGenerator):

    def generate(self):
        if self._page is None:
            self._get_goose()
        content = {'type': 'fetched'}
        try:
            content['content'] = self._from_goose_to_html()
            content['link'] = self._page.final_url
        except Exception:
            logger.exception("Could not rebuild parsed content for %r",
                             self.article)
            return {}
        if self.article.comments:
            content['comments'] = self.article.comments
        logger.debug('%r no special type found doing nothing', self.article)
        return content


class RedditContentGenerator(TruncatedContentGenerator):
    feed_type = FeedType.reddit

    def __init__(self, article):
        self._is_pure_reddit_post = None
        super().__init__(article)

    @property
    def is_pure_reddit_post(self):
        if self._is_pure_reddit_post is not None:
            return self._is_pure_reddit_post  # no re-computing
        self._is_pure_reddit_post = False
        if self.article.article_type is not None:
            return self._is_pure_reddit_post
        try:
            split = urllib.parse.urlsplit(self.article.link)
            paths = split.path.strip('/').split('/')
            if ('reddit.com' in split.netloc
                    and paths[0] == 'r' and paths[2] == 'comments'):
                self._is_pure_reddit_post = True
        except (AttributeError, IndexError):
            pass
        return self._is_pure_reddit_post

    def get_vector(self):
        if not self.is_pure_reddit_post:
            return super().get_vector()

    def generate(self):
        if not self.is_pure_reddit_post:
            return super().generate()
        return {}  # original reddit post, nothing to process


CONTENT_GENERATORS = {}


def feed_mapping(subcls_):
    if subcls_.feed_type is not None:
        CONTENT_GENERATORS[subcls_.feed_type] = subcls_
    if subcls_.article_type is not None:
        CONTENT_GENERATORS[subcls_.article_type] = subcls_


for subcls in ContentGenerator.__subclasses__():
    feed_mapping(subcls)
    for subsubcls in subcls.__subclasses__():
        feed_mapping(subsubcls)


@lru_cache()
def get_content_generator(article):
    if article.article_type and article.article_type in CONTENT_GENERATORS:
        return CONTENT_GENERATORS[article.article_type](article)

    if article.feed.feed_type \
            and article.feed.feed_type in CONTENT_GENERATORS:
        return CONTENT_GENERATORS[article.feed.feed_type](article)

    if article.feed.truncated_content:
        return TruncatedContentGenerator(article)

    return ContentGenerator(article)


def merge_content(cluster, article, content):
    if cluster.content.get('type') == 'fetched':
        return
    content = article.content_generator.generate()
    if content['type'] == cluster.content['type']:
        cluster.content = {'type': 'multi-%s' % cluster.content['type'],
                           'contents': [cluster.content, content]}
    elif cluster.content['type'] == 'multi-%s' % content['type']:
        cluster.content['contents'].append(content)
