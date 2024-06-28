import logging
import re
import urllib.parse
from functools import lru_cache

from typing import Optional
from goose3 import Goose
from jarr.bootstrap import conf
from jarr.controllers.article import to_vector
from jarr.lib.enums import ArticleType, FeedType
from jarr.lib.url_cleaners import remove_utm_tags
from jarr.lib.utils import clean_lang

logger = logging.getLogger(__name__)
IMG_ALT_MAX_LENGTH = 100
YOUTUBE_RE = re.compile(
    r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))"
    r"(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
)


def is_embedded_link(link):
    return YOUTUBE_RE.match(link)


def get_embedded_id(link):
    if match := YOUTUBE_RE.match(link):
        return match.group(5)


class ContentGenerator:
    article_type: Optional[ArticleType] = None
    feed_type: Optional[FeedType] = None

    def __init__(self, article):
        self.article = article
        self._page = None
        self.extracted_infos = {}

    def _get_goose(self):
        goose = Goose({"browser_user_agent": conf.crawler.user_agent})
        try:
            self._page = goose.extract(self.article.link)
        except Exception as error:
            msg = "something wrong happened while trying to fetch %r: %r"
            logger.error(msg, self.article.link, error)
        if not self._page:
            return False
        lang = self._page.opengraph.get("locale") or self._page.meta_lang
        self.extracted_infos["lang"] = clean_lang(lang)
        self.extracted_infos["link"] = self._page.final_url
        keywords = set(self._page.meta_keywords.split(", "))
        self.extracted_infos["tags"] = set(self._page.tags).union(keywords)
        self.extracted_infos["title"] = self._page.title
        return True

    def get_vector(self):
        if self._page is None:
            self._get_goose()
        if self._page and self.extracted_infos:
            return to_vector(self.extracted_infos, self._page)

    @staticmethod
    def generate():
        return {}

    def generate_and_merge(self, content):
        content = migrate_content(content)
        # if there is already some fetched content
        already_fetched = any(
            cnt.get("type") == "fetched"
            for cnt in content.get("contents") or []
        )
        if isinstance(self, TruncatedContentGenerator) and already_fetched:
            return content
        article_content = self.generate()
        if not article_content:
            return content
        content["contents"].append(article_content)
        return content


class MediaContentGenerator(ContentGenerator):

    @staticmethod
    def get_vector():
        return None

    @staticmethod
    def generate():
        return {}

    @staticmethod
    def generate_and_merge(content):
        return content


class ImageContentGenerator(MediaContentGenerator):
    article_type = ArticleType.image


class AudioContentGenerator(MediaContentGenerator):
    article_type = ArticleType.audio


class VideoContentGenerator(MediaContentGenerator):
    article_type = ArticleType.video


class EmbeddedContentGenerator(ContentGenerator):
    article_type = ArticleType.embedded

    @staticmethod
    def get_vector():
        return None

    def generate(self):
        yt_match = YOUTUBE_RE.match(self.article.link)
        if yt_match:
            msg = "%r constructing embedded youtube content from article"
            logger.info(msg, self.article)
            try:
                return {"type": "youtube", "link": yt_match.group(5)}
            except IndexError:
                pass
        else:
            msg = "embedded media not recognized %r"
            logger.warning(msg, self.article.link)
        return {}


class TruncatedContentGenerator(ContentGenerator):

    def generate(self):
        if self._page is None:
            self._get_goose()
        content = {"type": "fetched"}
        try:
            content["content"] = self._page.top_node_raw_html
            content["link"] = remove_utm_tags(self._page.final_url)
            content["title"] = self._page.title
        except Exception:
            msg = "Could not rebuild parsed content for %r"
            logger.exception(msg, self.article)
            return {}
        if self.article.comments:
            content["comments"] = self.article.comments
        logger.debug("%r no special type found doing nothing", self.article)
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
            paths = split.path.strip("/").split("/")
            if (
                "reddit.com" in split.netloc
                and paths[0] == "r"
                and paths[2] == "comments"
            ):
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

    if article.feed.feed_type and article.feed.feed_type in CONTENT_GENERATORS:
        return CONTENT_GENERATORS[article.feed.feed_type](article)

    if article.feed.truncated_content:
        return TruncatedContentGenerator(article)

    return ContentGenerator(article)


def migrate_content(content: dict):
    content = content or {"v": 2, "contents": []}
    if content.get("v") == 2:
        return content
    if content["type"] in {"image", "audio", "video"}:
        return {"v": 2, "contents": []}
    if content["type"] == "embedded":  # migrating original embedded
        content = {"type": content["player"], "link": content["videoId"]}
    return {"v": 2, "contents": [content]}
