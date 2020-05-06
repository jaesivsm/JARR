import html
import logging
import re

from jarr.lib.enums import ArticleType

logger = logging.getLogger(__name__)
IMG_ALT_MAX_LENGTH = 100
YOUTUBE_RE = re.compile(
        r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))'
        r'(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$')


def is_embedded_link(link):
    return YOUTUBE_RE.match(link)


def generate_content(article):
    success = False
    if not article.article_type:
        logger.debug('%r no special type found doing nothing', article)
        return success, {}
    content = {'type': article.article_type.value}
    if article.article_type is ArticleType.video:
        logger.debug('no action implemented for video yet')
    elif article.article_type is ArticleType.image:
        logger.info('%r constructing image content from article', article)
        content['alt'] = article.title or article.content
        content['alt'] = html.escape(content['alt'][:IMG_ALT_MAX_LENGTH])
        content['src'] = article.link
        success = True
    elif article.article_type is ArticleType.embedded:
        if YOUTUBE_RE.match(article.link):
            logger.info('%r constructing embedded youtube content from article',
                        article)
            content['player'] = 'youtube'
            try:
                content['videoId'] = YOUTUBE_RE.match(article.link).group(5)
                success = True
            except IndexError:
                pass
        else:
            logger.warning('embedded video not recognized %r', article.link)
    return success, content
