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


DEFAULT_UI_PORT = 8000
DEFAULT_URL = 'http://0.0.0.0:%d/' % DEFAULT_UI_PORT

conf = TheConf({'config_files': ['/etc/jarr/jarr.json', '~/.config/jarr.json'],
        'config_file_environ': ['JARR_CONFIG'],
        'source_order': ['env', 'files'],
        'parameters': [
            {'jarr_testing': {'default': False, 'type': bool}},
            {'cluster_default': [
                {'time_delta': {'default': 7, 'type': int}},
                {'tfidf_enabled': {'default': True, 'type': bool}},
                {'tfidf_min_sample_size': {'default': 10, 'type': int}},
                {'tfidf_min_score': {'default': .75, 'type': float}}]},
            {'timezone': {'default': 'Europe/Paris', 'type': str}},
            {'platform_url': {'default': DEFAULT_URL}},
            {'db': [{'pg_uri': {'default': 'postgresql://postgresql/jarr'}},
                    {'redis': [{'host': {'default': 'redis'}},
                               {'db': {'default': 0, 'type': int}},
                               {'port': {'default': 6379, 'type': int}},
                               {'password': {'default': None}}]}]},
            {'celery': [{'broker': {'default': 'amqp://rabbitmq//'}},
                        {'backend': {'default': 'redis://redis:6379/0'}},
                        {'BROKER_URL': {'default': 'amqp://rabbitmq//'}},
                        {'CELERY_TASK_SERIALIZER': {'default': 'json'}},
                        {'CELERY_RESULT_SERIALIZER': {'default': 'json'}},
                        {'CELERY_TASK_RESULT_EXPIRE': {'default': None}},
                        {'CELERY_TIMEZONE': {'default': 'Europe/Paris'}},
                        {'CELERY_ENABLE_UTC': {'default': True, 'type': bool}},
                        {'CELERY_IMPORTS': {'default': 'ep_celery'}},
                        {'CELERY_DEFAULT_QUEUE': {'default': 'jarr'}},
                        {'CELERY_DEFAULT_EXCHANGE': {'default': 'jarr'}}]},
            {'bundle_js': {'default': 'local'}},
            {'log': [{'level': {'default': logging.WARNING, 'type': int}},
                     {'path': {'default': "jarr.log"}}]},
            {'crawler': [{'idle_delay': {'default': 2 * 60, 'type': int}},
                         {'passwd': {'default': 'admin'}},
                         {'user_agent': {'default': 'Mozilla/5.0 (compatible; '
                                                    'jarr.info)'}},
                         {'timeout': {'default': 30, 'type': int}}]},
            {'plugins': [{'readability_key': {'default': ''}},
                         {'rss_bridge': {'default': ''}}]},
            {'auth': [{'secret_key': {'default': str(random.getrandbits(128))
                                      }},
                      {'jwt_header_prefix': {'default': 'JWT', 'type': str}},
                      {'expiration_sec': {'default': 3600, 'type': int}},
                      {'allow_signup': {'default': True, 'type': bool}}]},
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
                           {'port': {'default': DEFAULT_UI_PORT,
                                     'type': int}}]},
                      ]})


def is_secure_served():
    return PARSED_PLATFORM_URL.scheme == 'https'


def init_logging(log_path=None, log_level=logging.INFO, modules=(),
                 log_format='%(asctime)s %(levelname)s %(message)s'):

    if not modules:
        modules = 'root', 'wsgi', 'manager', 'jarr'
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


def init_db(echo=False):
    kwargs = {'echo': echo}
    new_engine = create_engine(conf.db.pg_uri, **kwargs)
    NewBase = declarative_base(new_engine)
    SessionMaker = sessionmaker(bind=new_engine)
    new_session = scoped_session(SessionMaker)

    return new_engine, new_session, NewBase


def init_models():
    from jarr import models
    return models


PARSED_PLATFORM_URL = urlparse(conf.platform_url)

engine, session, Base = init_db()
init_models()

init_logging(conf.log.path, log_level=conf.log.level)
init_logging(conf.log.path, log_level=logging.WARNING, modules=('the_conf',))
