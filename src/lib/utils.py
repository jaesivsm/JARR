import logging
import pytz
import re
import types
import urllib
from datetime import datetime
from hashlib import md5

import requests
from flask import request, url_for

from bootstrap import conf

logger = logging.getLogger(__name__)


def utc_now():
    return pytz.utc.localize(datetime.utcnow())


def default_handler(obj, role='admin'):
    """JSON handler for default query formatting"""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    if hasattr(obj, 'dump'):
        return obj.dump(role=role)
    if isinstance(obj, (set, frozenset, filter, types.GeneratorType)):
        return list(obj)
    if isinstance(obj, BaseException):
        return str(obj)
    raise TypeError("Object of type %s with value of %r "
                    "is not JSON serializable" % (type(obj), obj))


def try_keys(dico, *keys):
    for key in keys:
        if key in dico:
            return dico[key]
    return


def rebuild_url(url, base_split):
    split = urllib.parse.urlsplit(url)
    if split.scheme and split.netloc:
        return url  # url is fine
    new_split = urllib.parse.SplitResult(
            scheme=split.scheme or base_split.scheme,
            netloc=split.netloc or base_split.netloc,
            path=split.path, query=split.query, fragment=split.fragment)
    return urllib.parse.urlunsplit(new_split)


def to_hash(text):
    return md5(text.encode('utf8') if hasattr(text, 'encode') else text)\
            .hexdigest()


def clear_string(data):
    """
    Clear a string by removing HTML tags, HTML special caracters
    and consecutive white spaces (more that one).
    """
    p = re.compile('<[^>]+>')  # HTML tags
    q = re.compile('\s')  # consecutive white spaces
    return p.sub('', q.sub(' ', data))


def redirect_url(default='home'):
    return request.args.get('next') or request.referrer or url_for(default)


def jarr_get(url, headers=None, **kwargs):
    def_headers = {'User-Agent': conf.CRAWLER_USER_AGENT}
    if isinstance(headers, dict):
        def_headers.update(headers)
    request_kwargs = {'verify': False, 'allow_redirects': True,
                      'timeout': conf.CRAWLER_TIMEOUT, 'headers': def_headers}
    request_kwargs.update(kwargs)
    return requests.get(url, **request_kwargs)
