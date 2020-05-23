import html
from lxml import etree
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


def from_goose_to_html(article, encoding="utf8"):
    result = ""
    current_node = article.top_node
    while True:
        result += etree.tostring(current_node,
                                 encoding=encoding).decode(encoding)
        current_node = current_node.getnext()
        if current_node is None:
            break
    return result


def generate_content(article, parsed=None):
    success = False
    if not article.article_type:
        if parsed:
            content = {'type': 'fetched'}
            try:
                content['content'] = from_goose_to_html(parsed)
                content['link'] = parsed.final_url
                success = True
            except Exception:
                logger.exception("Could not rebuild parsed content for %r",
                                 article)
            if success and article.comments:
                content['comments'] = article.comments
            return success, content
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
            logger.info('%r constructing embedded youtube content '
                        'from article', article)
            content['player'] = 'youtube'
            try:
                content['videoId'] = YOUTUBE_RE.match(article.link).group(5)
                success = True
            except IndexError:
                pass
        else:
            logger.warning('embedded video not recognized %r', article.link)
    return success, content
