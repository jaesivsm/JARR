#! /usr/bin/env python
# -*- coding: utf-8 -

# required imports and code exection for basic functionning

from blinker import signal
import calendar
import logging
import os
import pytz
from urllib.parse import urlparse

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from lib.conf_handling import ConfObject

conf = ConfObject()
# handling on the fly migration to new conf style
if os.path.exists(os.path.abspath('conf.py')):
    import conf as oldconf
    for key in dir(oldconf):
        if key.startswith('_'):
            continue
        setattr(conf, key, getattr(oldconf, key))
    conf.write()
    os.remove(os.path.abspath('conf.py'))
conf.reload()

feed_creation = signal('feed_creation')
entry_parsing = signal('entry_parsing')
article_parsing = signal('article_parsing')


def set_logging(log_path=None, log_level=logging.INFO, modules=(),
                log_format='%(asctime)s %(levelname)s %(message)s'):

    if not modules:
        modules = ('root', 'bootstrap', 'runserver', 'lib',
                   'web', 'crawler', 'manager', 'plugins')
    if log_path:
        handler = logging.FileHandler(log_path)
    else:
        handler = logging.StreamHandler()
    formater = logging.Formatter(log_format)
    handler.setFormatter(formater)
    for logger_name in modules:
        logger = logging.getLogger(logger_name)
        logger.addHandler(handler)
        for handler in logger.handlers:
            handler.setLevel(log_level)
        logger.setLevel(log_level)


SQLITE_ENGINE = 'sqlite' in conf.SQLALCHEMY_DATABASE_URI
if os.environ.get('JARR_TESTING', False) == 'true':
    SQLITE_ENGINE = 'sqlite' in conf.TEST_SQLALCHEMY_DATABASE_URI
PARSED_PLATFORM_URL = urlparse(conf.PLATFORM_URL)


def is_secure_served():
    return PARSED_PLATFORM_URL.scheme == 'https'


set_logging(conf.LOG_PATH, log_level=conf.LOG_LEVEL)
db = SQLAlchemy()


def create_app():
    application = Flask('web')
    application.config.from_object(conf)
    if os.environ.get('JARR_TESTING', False) == 'true':
        application.debug = True
        test_db = application.config['TEST_SQLALCHEMY_DATABASE_URI']
        assert test_db
        application.config['SQLALCHEMY_DATABASE_URI'] = test_db
        conf.SQLALCHEMY_DATABASE_URI = test_db
        application.config['TESTING'] = True
        conf.CRAWLER_NBWORKER = 1
        application.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
    else:
        application.debug = conf.LOG_LEVEL <= logging.DEBUG
    application.config['SERVER_NAME'] = PARSED_PLATFORM_URL.netloc
    application.config['PREFERRED_URL_SCHEME'] = PARSED_PLATFORM_URL.scheme
    db.init_app(application)
    return application


def init_babel(application):
    from flask import request
    from flask_babel import Babel
    from babel import Locale

    babel = Babel(application)

    @babel.localeselector
    def get_flask_locale():
        from lib.utils import clean_lang
        for locale_id in request.accept_languages.values():
            try:
                return Locale(clean_lang(locale_id))
            except Exception:
                continue
        return Locale(conf.BABEL_DEFAULT_LOCALE)

    @babel.timezoneselector
    def get_flask_timezone():
        from flask_login import current_user
        return pytz.timezone(current_user.timezone
                             or conf.BABEL_DEFAULT_TIMEZONE)


def load_blueprints(application):
    from web import views
    with application.app_context():
        views.session_mgmt.load(application)
        application.register_blueprint(views.articles_bp)
        application.register_blueprint(views.cluster_bp)
        application.register_blueprint(views.feeds_bp)
        application.register_blueprint(views.feed_bp)
        application.register_blueprint(views.icon_bp)
        application.register_blueprint(views.admin_bp)
        application.register_blueprint(views.users_bp)
        application.register_blueprint(views.user_bp)
        application.register_blueprint(views.session_mgmt.oauth_bp)
        views.api.feed.load(application)
        views.api.category.load(application)
        views.api.cluster.load(application)
        views.api.article.load(application)
        views.home.load(application)
        views.views.load(application)

    application.jinja_env.filters['month_name'] \
            = lambda n: calendar.month_name[n]
    application.jinja_env.autoescape = False


def init_integrations():
    from lib import integrations

init_integrations()
