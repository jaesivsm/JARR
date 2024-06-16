#! /usr/bin/env python
# -*- coding: utf-8 -

# required imports and code exection for basic functionning

import logging

from prometheus_distributed_client import set_redis_conn
from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import registry, scoped_session, sessionmaker
from the_conf import TheConf

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
    mapper_registry = registry()
    new_engine = create_engine(
        conf.db.pg_uri,
        echo=echo,
        pool_size=conf.db.postgres.pool_size,
        max_overflow=conf.db.postgres.max_overflow,
        pool_recycle=conf.db.postgres.pool_recycle,
        pool_pre_ping=conf.db.postgres.pool_pre_ping,
        pool_use_lifo=conf.db.postgres.pool_use_lifo,
    )
    NewBase = mapper_registry.generate_base()
    new_session = scoped_session(sessionmaker(bind=new_engine))
    return mapper_registry, new_engine, new_session, NewBase


def init_models():
    from jarr import models
    return models


def commit_pending_sql(*args, **kwargs):
    session.commit()


def rollback_pending_sql(*args, **kwargs):
    session.rollback()


sqlalchemy_registry, engine, session, Base = init_db()
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
