from datetime import timedelta, timezone
import dateutil
import logging
import re

from bootstrap import conf
from lib.utils import to_hash, utc_now

logger = logging.getLogger(__name__)
MAX_AGE_RE = re.compile('max-age=([0-9]+)')
RFC_1123_FORMAT = '%a, %d %b %Y %X %Z'


def rfc_1123_utc(time_obj=None, delta=None):
    """return time obj or now formated in the RFC1123 style. Add time delta if
    present.
    """
    if time_obj is None:
        time_obj = utc_now()
    if delta is not None:
        time_obj += delta
    return time_obj.strftime(RFC_1123_FORMAT)


def extract_feed_info(headers):
    """providing the headers of a feed response, will calculate the headers
    needed for basic cache control.

    will extract etag and last modified.

    will calculate expires, with limit define in configuration file by
    FEED_MIN_EXPIRES and FEED_MAX_EXPIRES.
    """
    now = utc_now()
    min_expires = now + timedelta(seconds=conf.FEED_MIN_EXPIRES)
    max_expires = now + timedelta(seconds=conf.FEED_MAX_EXPIRES)

    feed_info = {'etag': headers.get('etag', ''),
                 'last_modified': headers.get('last-modified', rfc_1123_utc())}
    msg = "didn't found expiring mechanism, expiring at %r"
    if 'max-age' in headers.get('cache-control', ''):
        msg = 'found Cache-Control "max-age" header, expiring at %r'
        try:
            max_age = int(MAX_AGE_RE.search(headers['cache-control']).group(1))
        except Exception:
            pass
        else:
            feed_info['expires'] = now + timedelta(seconds=max_age)
    if 'expires' not in feed_info and headers.get('expires'):
        msg = "found Expires header, expiring at %r"
        try:
            expires = dateutil.parser.parse(headers['expires'])
            if expires.tzinfo:
                expires = expires.astimezone(timezone.utc)
            else:
                expires = expires.replace(tzinfo=timezone.utc)
        except Exception:
            pass
        else:
            feed_info['expires'] = expires

    if not feed_info.get('expires'):
        feed_info['expires'] = now + timedelta(
                seconds=conf.FEED_DEFAULT_EXPIRES)
    logger.info(msg, feed_info['expires'].isoformat())
    if max_expires < feed_info['expires']:
        logger.info("expiring too late, forcing expiring at %r",
                    max_expires.isoformat())
        feed_info['expires'] = max_expires
    if feed_info['expires'] < min_expires:
        min_ex_plus_buffer = min_expires \
                + timedelta(seconds=conf.FEED_MIN_EXPIRES / 2)
        logger.info("expiring too early, forcing expiring at %r",
                    min_ex_plus_buffer.isoformat())
        feed_info['expires'] = min_ex_plus_buffer
    return feed_info


def prepare_headers(feed):
    """For a known feed, will construct some header dictionnary"""
    headers = {'User-Agent': conf.CRAWLER_USER_AGENT}
    if feed.get('last_modified'):
        headers['If-Modified-Since'] = feed['last_modified']
    if feed.get('etag') and 'jarr' not in feed['etag']:
        headers['If-None-Match'] = feed['etag']
    logger.debug('%r %r - calculated headers %r',
                    feed['id'], feed['title'], headers)
    return headers


def response_match_cache(response, feed):
    if 'etag' not in response.headers:
        logger.debug('%r %r - manually generating etag',
                        feed['id'], feed['title'])
        response.headers['etag'] = 'jarr/"%s"' % to_hash(response.text)
    if response.headers['etag'] and feed['etag'] \
            and response.headers['etag'] == feed['etag']:
        if 'jarr' in feed['etag']:
            logger.info("%r %r - calculated hash matches (%d)",
                        feed['id'], feed['title'], response.status_code)
        else:
            logger.info("%r %r - feed responded with same etag (%d)",
                        feed['id'], feed['title'], response.status_code)
        return True
    return False
