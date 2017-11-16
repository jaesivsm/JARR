import logging
import pytz
import re
import types
import urllib
from enum import Enum
from datetime import datetime
from hashlib import md5

import requests
from flask import request, url_for
from werkzeug.exceptions import HTTPException

from bootstrap import conf

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


def default_handler(obj, role='admin'):
    """JSON handler for default query formatting"""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    if hasattr(obj, 'dump'):
        return obj.dump(role=role)
    if isinstance(obj, (set, frozenset, filter, types.GeneratorType)):
        return list(obj)
    if isinstance(obj, HTTPException):
        return "%d: %s" % (obj.code, obj.name)
    if isinstance(obj, BaseException):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.name
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
    tag = re.compile(r'<[^>]+>')  # HTML tags
    whitespace = re.compile(r'\s')  # consecutive white spaces
    return tag.sub('', whitespace.sub(' ', data))


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
