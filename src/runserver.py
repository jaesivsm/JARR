#! /usr/bin/env python
# -*- coding: utf-8 -*-
import calendar

import pytz
from babel import Locale
from flask import request
from flask_babel import Babel
from flask_login import current_user

from bootstrap import application, conf

if conf.ON_HEROKU:
    from flask_sslify import SSLify
    SSLify(application)

babel = Babel(application)


@babel.localeselector
def get_flask_locale():
    for locale_id in request.accept_languages.values():
        try:
            return Locale(locale_id)
        except Exception:
            if '-' not in locale_id:
                continue
            try:
                return Locale(locale_id.replace('-', '_'))
            except Exception:
                continue
    return Locale(conf.BABEL_DEFAULT_LOCALE)


@babel.timezoneselector
def get_flask_timezone():
    return pytz.timezone(current_user.timezone or conf.BABEL_DEFAULT_TIMEZONE)


# Jinja filters
application.jinja_env.filters['month_name'] = lambda n: calendar.month_name[n]
application.jinja_env.autoescape = False

# Views
with application.app_context():
    from web import views
    application.register_blueprint(views.articles_bp)
    application.register_blueprint(views.cluster_bp)
    application.register_blueprint(views.feeds_bp)
    application.register_blueprint(views.feed_bp)
    application.register_blueprint(views.icon_bp)
    application.register_blueprint(views.admin_bp)
    application.register_blueprint(views.users_bp)
    application.register_blueprint(views.user_bp)


if __name__ == '__main__':  # pragma: no cover
    application.run(host=conf.WEBSERVER_HOST,
                    port=conf.WEBSERVER_PORT,
                    debug=True)
