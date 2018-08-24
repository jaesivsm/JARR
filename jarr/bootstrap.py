#! /usr/bin/env python
# -*- coding: utf-8 -

# required imports and code exection for basic functionning

import logging
import random
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from the_conf import TheConf

conf = TheConf({'config_files': ['/etc/jarr.json', '~/.config/jarr.json'],
        'source_order': ['env', 'cmd', 'files'],
        'parameters': [
            {'jarr_testing': {'default': False, 'type': bool}},
            {'cluster_tfidf_min_score': {'default': .75, 'type': float}},
            {'timezone': {'default': 'Europe/Paris', 'type': str}},
            {'platform_url': {'default': 'http://0.0.0.0:5000/'}},
            {'sqlalchemy': [{'db_uri': {}},
                            {'test_uri': {'default': 'sqlite:///:memory:'}}]},
            {'secret_key': {'default': str(random.getrandbits(128))}},
            {'bundle_js': {'default': 'local'}},
            {'log': [{'level': {'default': logging.WARNING, 'type': int}},
                     {'path': {'default': "jarr.log"}}]},
            {'crawler': [{'login': {'default': 'admin'}},
                         {'passwd': {'default': 'admin'}},
                         {'type': {'default': 'http'}},
                         {'resolv': {'type': bool, 'default': False}},
                         {'user_agent': {
                             'default': 'https://github.com/jaesivsm/JARR'}},
                         {'timeout': {'default': 30, 'type': int}}]},
            {'plugins': [{'readability_key': {'default': ''}},
                         {'rss_bridge': {'default': ''}}]},
            {'auth': [{'allow_signup': {'default': True, 'type': bool}}]},
            {'oauth': [{'allow_signup': {'default': False, 'type': bool}},
                    {'twitter': [{'id': {'default': ''}},
                                 {'secret': {'default': ''}}]},
                    {'facebook': [{'id': {'default': ''}},
                                  {'secret': {'default': ''}}]},
                    {'google': [{'id': {'default': ''}},
                                {'secret': {'default': ''}}]},
                    {'linuxfr': [{'id': {'default': ''}},
                                 {'secret': {'default': ''}}]}]},
            {'notification': [{'email': {'default': ''}},
                              {'host': {'default': ''}},
                              {'starttls': {'type': bool, 'default': True}},
                              {'port': {'type': int, 'default': 587}},
                              {'login': {'default': ''}},
                              {'password': {'default': ''}}]},
            {'feed': [{'error_max': {'type': int, 'default': 6}},
                      {'error_threshold': {'type': int, 'default': 3}},
                      {'min_expires': {'type': int, 'default': 60 * 10}},
                      {'max_expires': {'type': int, 'default': 60 * 60 * 4}},
                      {'stop_fetch': {'default': 30, 'type': int}}]},
            {'webserver': [{'host': {'default': '0.0.0.0'}},
                           {'port': {'default': 5000, 'type': int}}]},
                      ]})

# utilities


def is_secure_served():
    return PARSED_PLATFORM_URL.scheme == 'https'

# init func


def init_logging(log_path=None, log_level=logging.INFO, modules=(),
                 log_format='%(asctime)s %(levelname)s %(message)s'):

    if not modules:
        modules = ('root', 'wsgi', 'manager',
                   'jarr', 'jarr_crawler', 'jarr_common')
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


def init_db(is_sqlite, echo=False):  # pragma: no cover
    kwargs = {'echo': echo}
    if is_sqlite:
        kwargs['connect_args'] = {'check_same_thread': False}
    if conf.jarr_testing:
        new_engine = create_engine(conf.sqlalchemy.test_uri, **kwargs)
    else:
        new_engine = create_engine(conf.sqlalchemy.db_uri, **kwargs)
    NewBase = declarative_base(new_engine)
    SessionMaker = sessionmaker(bind=new_engine)
    new_session = scoped_session(SessionMaker)

    return new_engine, new_session, NewBase


def init_models():
    from jarr import models
    return models


SQLITE_ENGINE = 'sqlite' in (conf.sqlalchemy.test_uri
            if conf.jarr_testing else conf.sqlalchemy.db_uri)
PARSED_PLATFORM_URL = urlparse(conf.platform_url)

engine, session, Base = init_db(SQLITE_ENGINE)
init_models()

init_logging(conf.log.path, log_level=conf.log.level)
init_logging(conf.log.path, log_level=logging.WARNING, modules=('the_conf',))
