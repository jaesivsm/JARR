#! /usr/bin/env python
# -*- coding: utf-8 -

# required imports and code exection for basic functionning

import os
import conf
import logging
from urllib.parse import urlsplit
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


def set_logging(log_path, log_level=logging.INFO,
                log_format='%(asctime)s %(levelname)s %(message)s'):
    formater = logging.Formatter(log_format)
    handler = logging.FileHandler(log_path)
    handler.setFormatter(formater)
    for logger_name in ('bootstrap', 'web', 'manager', 'runserver'):
        logger = logging.getLogger(logger_name)
        logger.addHandler(handler)
        logger.setLevel(log_level)

# Create Flask application
application = Flask('web')
API_ROOT = '/api/v2.0'
if os.environ.get('JARR_TESTING', False) == 'true':
    application.debug = True
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    application.config['TESTING'] = True
else:
    application.debug = conf.LOG_LEVEL <= logging.DEBUG
    application.config['SQLALCHEMY_DATABASE_URI'] \
            = conf.SQLALCHEMY_DATABASE_URI

scheme, domain, _, _, _ = urlsplit(conf.PLATFORM_URL)
application.config['SERVER_NAME'] = domain
application.config['PREFERRED_URL_SCHEME'] = scheme
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

set_logging(conf.LOG_PATH, log_level=conf.LOG_LEVEL)

# Create dummy secrey key so we can use sessions
application.config['SECRET_KEY'] = getattr(conf, 'WEBSERVER_SECRET', None)
if not application.config['SECRET_KEY']:
    application.config['SECRET_KEY'] = os.urandom(12)

application.config['RECAPTCHA_USE_SSL'] = True
application.config['RECAPTCHA_PUBLIC_KEY'] = conf.RECAPTCHA_PUBLIC_KEY
application.config['RECAPTCHA_PRIVATE_KEY'] = conf.RECAPTCHA_PRIVATE_KEY

db = SQLAlchemy(application)
