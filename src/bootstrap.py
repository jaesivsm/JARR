#! /usr/bin/env python
# -*- coding: utf-8 -

# required imports and code exection for basic functionning

import os
import conf
import logging
from urllib.parse import urlparse
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


def to_log_level(level):
    return {'debug': logging.DEBUG,
            'info': logging.INFO,
            'warn': logging.WARN,
            'error': logging.ERROR,
            'fatal': logging.FATAL}.get(str(level).lower(), logging.WARN)


conf.LOG_LEVEL = to_log_level(conf.LOG_LEVEL)


def set_logging(log_path=None, log_level=logging.INFO, modules=(),
                log_format='%(asctime)s %(levelname)s %(message)s'):

    if not modules:
        modules = ('root', 'bootstrap', 'runserver',
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

# Create Flask application
application = Flask('web')
application.config.from_object(conf)
if os.environ.get('JARR_TESTING', False) == 'true':
    application.debug = True
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    application.config['TESTING'] = True
    conf.CRAWLER_NBWORKER = 1
else:
    application.debug = conf.LOG_LEVEL <= logging.DEBUG

PARSED_PLATFORM_URL = urlparse(conf.PLATFORM_URL)
application.config['SERVER_NAME'] = PARSED_PLATFORM_URL.netloc
application.config['PREFERRED_URL_SCHEME'] = PARSED_PLATFORM_URL.scheme

def is_secure_served():
    return PARSED_PLATFORM_URL.scheme == 'https'

set_logging(conf.LOG_PATH, log_level=conf.LOG_LEVEL)

db = SQLAlchemy(application)
