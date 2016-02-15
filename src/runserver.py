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
application.jinja_env.globals['conf'] = conf

# Views
with application.app_context():
    from web.views import views, home, session_mgmt, api
    from web.views.article import article_bp, articles_bp
    from web.views.feed import feed_bp, feeds_bp
    from web.views.category import category_bp, categories_bp
    from web.views.icon import icon_bp
    from web.views.admin import admin_bp
    from web.views.user import user_bp, users_bp
    application.register_blueprint(articles_bp)
    application.register_blueprint(article_bp)
    application.register_blueprint(feeds_bp)
    application.register_blueprint(feed_bp)
    application.register_blueprint(categories_bp)
    application.register_blueprint(category_bp)
    application.register_blueprint(icon_bp)
    application.register_blueprint(admin_bp)
    application.register_blueprint(users_bp)
    application.register_blueprint(user_bp)


if __name__ == '__main__':  # pragma: no cover
    application.run(host=conf.WEBSERVER_HOST,
                    port=conf.WEBSERVER_PORT,
                    debug=True)
