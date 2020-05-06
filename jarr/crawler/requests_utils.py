import logging


from jarr.lib.utils import to_hash

logger = logging.getLogger(__name__)


def response_etag_match(feed, resp):
    if feed.etag and resp.headers.get('etag'):
        if feed.etag.startswith('jarr/'):
            return False  # it's a jarr generated etag
        if resp.headers['etag'] == feed.etag:
            logger.info("feed responded with same etag (%d)", resp.status_code)
            return True
    return False


def response_calculated_etag_match(feed, resp):
    if ('jarr/"%s"' % to_hash(resp.text)) == feed.etag:
        logger.info("calculated hash matches (%d)", resp.status_code)
        return True
    return False
