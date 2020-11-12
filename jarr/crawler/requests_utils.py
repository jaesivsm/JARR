import logging

from jarr.lib.utils import digest

logger = logging.getLogger(__name__)


def response_etag_match(feed, resp):
    if feed.etag and resp.headers.get('etag'):
        if feed.etag.startswith('jarr/'):
            return False  # it's a jarr generated etag
        if resp.headers['etag'] == feed.etag:
            logger.info("%r: responded with same etag (%d)",
                        feed, resp.status_code)
            return True
    return False


def response_calculated_etag_match(feed, resp):
    if ('jarr/"%s"' % digest(resp.text)) == feed.etag:
        logger.info("%r: calculated hash matches (%d)",
                    feed, resp.status_code)
        return True
    return False
