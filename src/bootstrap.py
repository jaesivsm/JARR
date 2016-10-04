#! /usr/bin/env python
# -*- coding: utf-8 -

# required imports and code exection for basic functionning

import os
import logging
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
    conf.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
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
