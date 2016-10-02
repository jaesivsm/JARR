import pytz
from functools import wraps
from datetime import datetime
from flask import request, Response, make_response
from flask_babel import get_locale
from babel.dates import format_datetime, format_timedelta
from web.views.common import jsonify
from lib.utils import to_hash


def etag_match(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if isinstance(response, Response):
            etag = to_hash(response.data)
            headers = response.headers
        elif type(response) is str:
            etag = to_hash(response)
            headers = {}
        else:
            return response
        if request.headers.get('if-none-match') == etag:
            response = Response(status=304)
            response.headers['Cache-Control'] \
                    = headers.get('Cache-Control', 'pragma: no-cache')
        elif not isinstance(response, Response):
            response = make_response(response)
        response.headers['etag'] = etag
        return response
    return wrapper


def _iter_on_rows(rows, now, locale):
    for row in rows:
        row['selected'] = False
        row['date'] = format_datetime(
                pytz.utc.localize(row['main_date']), locale=locale)
        row['rel_date'] = format_timedelta(row['main_date'] - now,
                threshold=1.1, add_direction=True, locale=locale)
        yield row


@jsonify
def clusters_to_json(clusters):
    return {'clusters': _iter_on_rows(clusters,
                                      datetime.utcnow(), get_locale())}
