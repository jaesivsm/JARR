import logging
import re
from datetime import timedelta, timezone

import dateutil.parser

from jarr.bootstrap import conf
from jarr.lib.const import FEED_ACCEPT_HEADERS
from jarr.lib.utils import rfc_1123_utc, to_hash, utc_now

logger = logging.getLogger(__name__)
MAX_AGE_RE = re.compile('max-age=([0-9]+)')


def _extract_max_age(headers, feed_info, now):
    if 'max-age' in headers.get('cache-control', ''):
        try:
            max_age = int(MAX_AGE_RE.search(headers['cache-control']).group(1))
            feed_info['expires'] = now + timedelta(seconds=max_age)
        except Exception:
            logger.exception("something went wrong while parsing max-age")


def _extract_expires(headers, feed_info):
    if headers.get('expires'):
        try:
            expires = dateutil.parser.parse(headers['expires'])
            if expires.tzinfo:
                expires = expires.astimezone(timezone.utc)
            else:
                expires = expires.replace(tzinfo=timezone.utc)
            feed_info['expires'] = expires
        except Exception:
            logger.exception("something went wrong while parsing expires")


def extract_feed_info(headers, text=None):
    """
    Providing the headers of a feed response,
    will calculate the headers needed for basic cache control,
    will extract etag and last modified,
    and will calculate expires, with limit define in configuration file by
    FEED_MIN_EXPIRES and FEED_MAX_EXPIRES.
    """
    now = utc_now()
    min_expires = now + timedelta(seconds=conf.feed.min_expires)
    max_expires = now + timedelta(seconds=conf.feed.max_expires)

    feed_info = {'etag': headers.get('etag', ''),
                 'last_modified': headers.get('last-modified', rfc_1123_utc())}
    if text and not feed_info['etag']:
        feed_info['etag'] = 'jarr/"%s"' % to_hash(text)

    _extract_max_age(headers, feed_info, now)
    if 'expires' not in feed_info:
        _extract_expires(headers, feed_info)

    if not feed_info.get('expires'):
        feed_info['expires'] = None
    elif max_expires < feed_info['expires']:
        logger.info("expiring too late, forcing expiring at %r",
                    max_expires.isoformat())
        feed_info['expires'] = max_expires
    elif feed_info['expires'] < min_expires:
        min_exp_w_buffer = now + timedelta(seconds=conf.feed.min_expires)
        logger.info("expiring too early, forcing expiring at %r",
                    min_exp_w_buffer.isoformat())
        feed_info['expires'] = min_exp_w_buffer
    return feed_info


def prepare_headers(feed):
    """For a known feed, will construct some header dictionnary"""
    headers = {'User-Agent': conf.crawler.user_agent,
               'Accept': FEED_ACCEPT_HEADERS}
    if feed.last_modified:
        headers['If-Modified-Since'] = feed.last_modified
    if feed.etag and 'jarr' not in feed.etag:
        headers['If-None-Match'] = feed.etag
    if 'If-Modified-Since' in headers or 'If-None-Match' in headers:
        headers['A-IM'] = 'feed'
    logger.debug('%r %r - calculated headers %r', feed.id, feed.title, headers)
    return headers
