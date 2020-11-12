#! /usr/bin/env python
# -*- coding: utf-8 -

# required imports and code exection for basic functionning

import logging
from redis import Redis

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from the_conf import TheConf

from prometheus_distributed_client import set_redis_conn

conf = TheConf('jarr/metaconf.yml')


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
set_redis_conn(host=conf.db.metrics.host,
               db=conf.db.metrics.db,
               port=conf.db.metrics.port)
init_logging(conf.log.path, log_level=logging.WARNING,
             modules=('the_conf',))
init_logging(conf.log.path, log_level=conf.log.level)
REDIS_CONN = Redis(host=conf.db.redis.host,
                   db=conf.db.redis.db,
                   port=conf.db.redis.port)
