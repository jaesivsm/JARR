import json
import asyncio
import logging
from functools import partial

import requests

from jarr_common.utils import default_handler, to_hash
from jarr_crawler.bootstrap import conf

logger = logging.getLogger(__name__)


def query_jarr(method_name, urn, pool=None, data=None):
    """A wrapper for internal call, method should be ones you can find
    on requests (header, post, get, options, ...), urn the distant
    resources you want to access on jarr, and data, the data you wanna
    transmit."""
    auth = conf.crawler.login, conf.crawler.passwd
    loop = asyncio.get_event_loop()
    if data is None:
        data = {}
    method = getattr(requests, method_name)
    url = "/".join(str_.strip('/') for str_ in (conf.platform_url,
                   conf.api_root.strip('/'), urn))

    future = loop.run_in_executor(None,
            partial(method, url, auth=auth, timeout=conf.crawler.timeout,
                    data=json.dumps(data, default=default_handler),
                    headers={'Content-Type': 'application/json',
                             'User-Agent': conf.crawler.user_agent}))
    if pool is not None:
        pool.append(future)
    return future


def response_etag_match(feed, resp):
    if feed.get('etag') and resp.headers.get('etag'):
        if feed['etag'].startswith('jarr/'):
            return False  # it's a jarr generated etag
        if resp.headers['etag'] == feed['etag']:
            logger.info("feed responded with same etag (%d)", resp.status_code)
            return True
    return False


def response_calculated_etag_match(feed, resp):
    if ('jarr/"%s"' % to_hash(resp.text)) == feed.get('etag'):
        logger.info("calculated hash matches (%d)", resp.status_code)
        return True
    return False
