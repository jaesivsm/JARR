import re
import logging
from jarr.lib.enums import ArticleType

logger = logging.getLogger(__name__)
YOUTUBE_VIDEO_RE = re.compile(
        r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))'
        r'(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$')


def is_embedded_link(link):
    return YOUTUBE_VIDEO_RE.match(link)


def generate_content(article):
    if not article.article_type:
        logger.debug('%r no special type found doing nothing', article)
        return
    if article.article_type is ArticleType.video:
        logger.debug('no action implemented for video yet')
        return
    if article.article_type is ArticleType.image:
        logger.info('%r constructing image content from article', article)
        return '<img alt="" src="%s" />' % article.link
    if article.article_type is ArticleType.embedded:
        if YOUTUBE_VIDEO_RE.match(article.link):
            logger.info('%r constructing embedded youtube content from article',
                        article)
            return
        logger.warning('embedded video not recognized %r', article.link)
