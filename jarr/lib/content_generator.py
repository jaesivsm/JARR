import re
import logging

logger = logging.getLogger(__name__)
YOUTUBE_VIDEO_RE = re.compile(
        r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$')


def is_embedded_link(link):
    return YOUTUBE_VIDEO_RE.match(link)


def generate_content(article):
    if not article.article_type:
        logger.debug('%r no special type found doing nothing', article)
        return
