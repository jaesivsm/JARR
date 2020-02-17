import logging
import re
import types
import urllib
from datetime import datetime
from enum import Enum
from hashlib import md5

import pytz
import requests

logger = logging.getLogger(__name__)
RFC_1123_FORMAT = '%a, %d %b %Y %X %Z'
LANG_FORMAT = re.compile('^[a-z]{2}(_[A-Z]{2})?$')
CORRECTABLE_LANG_FORMAT = re.compile('^[A-z]{2}(.[A-z]{2})?.*$')


def utc_now():
    return pytz.utc.localize(datetime.utcnow())


def clean_lang(lang):
    if LANG_FORMAT.match(lang or ''):
        return lang
    if not CORRECTABLE_LANG_FORMAT.match(lang or ''):
        return None
    proper_lang = lang[0:2].lower()
    if len(lang) >= 5:
        proper_lang = "%s_%s" % (proper_lang, lang[3:5].upper())
    return proper_lang


def rfc_1123_utc(time_obj=None, delta=None):
    """return time obj or now formated in the RFC1123 style. Add time delta if
    present.
    """
    if time_obj is None:
        time_obj = utc_now()
    if delta is not None:
        time_obj += delta
    return time_obj.strftime(RFC_1123_FORMAT)


def default_handler(obj):
    """JSON handler for default query formatting"""
    if isinstance(obj, (set, frozenset, filter, types.GeneratorType)):
        return list(obj)
    if isinstance(obj, Enum):
        return obj.value
    raise TypeError("Object of type %s with value of %r "
                    "is not JSON serializable" % (type(obj), obj))


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


def jarr_get(url, timeout, user_agent, headers=None, **kwargs):
    def_headers = {'User-Agent': user_agent}
    if headers is not None:
        def_headers.update(headers)
    request_kwargs = {'verify': False, 'allow_redirects': True,
                      'timeout': timeout, 'headers': def_headers}
    request_kwargs.update(kwargs)
    return requests.get(url, **request_kwargs)
