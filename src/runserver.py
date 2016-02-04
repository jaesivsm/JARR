#! /usr/bin/env python
# -*- coding: utf-8 -*-
import calendar
from bootstrap import conf, application, populate_g
from flask.ext.babel import Babel
from flask.ext.babel import format_datetime

if conf.ON_HEROKU:
    from flask_sslify import SSLify
    SSLify(application)

babel = Babel(application)


# Jinja filters
def month_name(month_number):
    return calendar.month_name[month_number]
application.jinja_env.filters['month_name'] = month_name
application.jinja_env.filters['datetime'] = format_datetime
application.jinja_env.globals['conf'] = conf

# Views
from flask.ext.restful import Api
from flask import g

with application.app_context():
    populate_g()
    g.api = Api(application, prefix='/api/v2.0')
    g.babel = babel

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


if __name__ == '__main__':
    application.run(host=conf.WEBSERVER_HOST,
                    port=conf.WEBSERVER_PORT,
                    debug=True)
