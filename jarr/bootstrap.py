#! /usr/bin/env python
# -*- coding: utf-8 -

# required imports and code exection for basic functionning

import logging
import random

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from the_conf import TheConf


conf = TheConf({'config_files': ['/etc/jarr/jarr.json', '~/.config/jarr.json'],
        'config_file_environ': ['JARR_CONFIG'],
        'source_order': ['env', 'files'],
        'parameters': [
            {'jarr_testing': {'default': False, 'type': bool}},
            {'debug': {'default': True, 'type': bool}},
            {'cluster_default': [
                {'time_delta': {'default': 20, 'type': int}},
                {'tfidf_enabled': {'default': True, 'type': bool}},
                {'tfidf_min_sample_size': {'default': 10, 'type': int}},
                {'tfidf_min_score': {'default': .75, 'type': float}}]},
            {'timezone': {'default': 'Europe/Paris', 'type': str}},
            {'app': [{'url': {'default': 'http://0.0.0.0:3000'}}]},
            {'api': [{'scheme': {'default': 'http'}}]},
            {'db': [{'pg_uri': {'default': 'postgresql://postgresql/jarr'}},
                    {'redis': [{'host': {'default': 'redis'}},
                               {'db': {'default': 0, 'type': int}},
                               {'port': {'default': 6379, 'type': int}},
                               {'password': {'default': None}}]}]},
            {'celery': [{'broker': {'default': 'amqp://rabbitmq//'}},
                        {'backend': {'default': 'redis://redis:6379/0'}},
                        {'broker_url': {'default': 'amqp://rabbitmq//'}},
                        {'task_serializer': {'default': 'json'}},
                        {'result_serializer': {'default': 'json'}},
                        {'timezone': {'default': 'Europe/Paris'}},
                        {'enable_utc': {'default': True, 'type': bool}},
                        {'imports': {'default': ('ep_celery',
                                                 'jarr.crawler.main'),
                                     'type': tuple}},
                        {'task_default_queue': {'default': 'jarr'}},
                        {'task_default_exchange': {'default': 'jarr'}}]},
            {'log': [{'level': {'default': logging.WARNING, 'type': int}},
                     {'path': {'default': "jarr.log"}}]},
            {'crawler': [{'idle_delay': {'default': 2 * 60, 'type': int}},
                         {'user_agent': {'default': 'Mozilla/5.0 (compatible; '
                                                    'jarr.info)'}},
                         {'timeout': {'default': 30, 'type': int}}]},
            {'plugins': [{'readability_key': {'default': ''}},
                         {'rss_bridge': {'default': ''}}]},
            {'auth': [{'secret_key': {'default': str(random.getrandbits(128))
                                      }},
                      {'jwt_header_prefix': {'default': 'JWT', 'type': str}},
                      {'expiration_sec': {'default': 24 * 3600, 'type': int}},
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
                      ]})


def is_secure_served():
    return conf.api.scheme == 'https'


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


def commit_pending_sql(*args, **kwargs):
    session.commit()


def rollback_pending_sql(*args, **kwargs):
    session.rollback()


engine, session, Base = init_db()
init_models()

init_logging(conf.log.path, log_level=logging.WARNING,
             modules=('the_conf',))
init_logging(conf.log.path, log_level=conf.log.level)
