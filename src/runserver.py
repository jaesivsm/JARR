#! /usr/bin/env python
# -*- coding: utf-8 -*-
import calendar
from flask import request
from flask.ext.babel import Babel
from bootstrap import conf, application

if conf.ON_HEROKU:
    from flask_sslify import SSLify
    SSLify(application)

babel = Babel(application)


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(conf.LANGUAGES.keys())


@babel.timezoneselector
def get_timezone():
    try:
        return conf.TIME_ZONE[get_locale()]
    except:
        return conf.TIME_ZONE["en"]

# Jinja filters
application.jinja_env.filters['month_name'] = lambda n: calendar.month_name[n]

# Views
with application.app_context():
    from web import views
    application.register_blueprint(views.articles_bp)
    application.register_blueprint(views.article_bp)
    application.register_blueprint(views.feeds_bp)
    application.register_blueprint(views.feed_bp)
    application.register_blueprint(views.categories_bp)
    application.register_blueprint(views.category_bp)
    application.register_blueprint(views.icon_bp)
    application.register_blueprint(views.admin_bp)
    application.register_blueprint(views.users_bp)
    application.register_blueprint(views.user_bp)


if __name__ == '__main__':  # pragma: no cover
    application.run(host=conf.WEBSERVER_HOST,
                    port=conf.WEBSERVER_PORT,
                    debug=True)
