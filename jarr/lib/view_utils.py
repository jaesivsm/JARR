from functools import wraps

from flask import Response, get_flashed_messages, make_response, request
from jarr_common.utils import to_hash, utc_now

from jarr.views.common import jsonify, fmt_datetime, fmt_timedelta

ACCEPTED_LEVELS = {'success', 'info', 'warning', 'error'}


def etag_match(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if isinstance(response, Response):
            etag = to_hash(response.data)
            headers = response.headers
        elif isinstance(response, str):
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


def _iter_on_rows(rows):
    now = utc_now()
    for row in rows:
        row['selected'] = False
        row['date'] = fmt_datetime(row['main_date'])
        row['rel_date'] = fmt_timedelta(row['main_date'] - now, threshold=1.1)
        yield row


def get_notifications():
    for msg in get_flashed_messages(with_categories=True):
        yield {'level': msg[0] if msg[0] in ACCEPTED_LEVELS else 'info',
               'message': msg[1]}


@jsonify
def clusters_to_json(clusters):
    return {'clusters': _iter_on_rows(clusters),
            'notifications': get_notifications()}
