from functools import wraps

from babel.dates import format_datetime, format_timedelta
from flask import Response, get_flashed_messages, make_response, request
from flask_babel import get_locale

from lib.utils import to_hash, utc_now
from web.views.common import jsonify

ACCEPTED_LEVELS = {'success', 'info', 'warning', 'error'}


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


def _iter_on_rows(rows, locale):
    now = utc_now()
    for row in rows:
        row['selected'] = False
        row['date'] = format_datetime(row['main_date'], locale=locale)
        row['rel_date'] = format_timedelta(row['main_date'] - now,
                threshold=1.1, add_direction=True, locale=locale)
        yield row


def get_notifications():
    for msg in get_flashed_messages(with_categories=True):
        yield {'level': msg[0] if msg[0] in ACCEPTED_LEVELS else 'info',
               'message': msg[1]}


@jsonify
def clusters_to_json(clusters):
    return {'clusters': _iter_on_rows(clusters, get_locale()),
            'notifications': get_notifications()}
