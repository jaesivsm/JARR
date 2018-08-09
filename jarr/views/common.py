import json
from functools import wraps

from babel.dates import format_datetime, format_timedelta
from flask import Response, current_app
from flask_babel import get_timezone, get_locale
from flask_login import login_user
from flask_principal import (Identity, Permission, RoleNeed, identity_changed,
                             session_identity_loader)

from jarr_common.utils import default_handler

admin_role = RoleNeed('admin')
api_role = RoleNeed('api')

admin_permission = Permission(admin_role)
api_permission = Permission(api_role)


def fmt_datetime(datetime):
    return format_datetime(datetime.astimezone(get_timezone()),
                           locale=get_locale())


def fmt_timedelta(timedelta, **kwargs):
    return format_timedelta(timedelta,
            add_direction=True, locale=get_locale(), **kwargs)


def scoped_default_handler():
    if admin_permission.can():
        role = 'admin'
    elif api_permission.can():
        role = 'api'
    else:
        role = 'user'

    @wraps(default_handler)
    def wrapper(obj):
        return default_handler(obj, role=role)
    return wrapper


def jsonify(func):
    """Will cast results of func as a result, and try to extract
    a status_code for the Response object"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        status_code = 200
        result = func(*args, **kwargs)
        if isinstance(result, Response):
            return result
        elif isinstance(result, tuple):
            result, status_code = result
        return Response(json.dumps(result, default=scoped_default_handler()),
                        mimetype='application/json', status=status_code)
    return wrapper


def login_user_bundle(user):
    login_user(user)
    identity_changed.send(current_app._get_current_object(),
                          identity=Identity(user.id))
    session_identity_loader()
