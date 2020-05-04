#! /usr/bin/env python
# -*- coding: utf-8 -*-
from wsgiref.simple_server import make_server

from celery import Celery, signals
from prometheus_client import make_wsgi_app

from jarr.bootstrap import conf, commit_pending_sql, rollback_pending_sql

celery_app = Celery(broker=conf.celery.broker_url,
                    config_source=conf.celery)
signals.task_success.connect(commit_pending_sql)
signals.task_failure.connect(rollback_pending_sql)

if not conf.jarr_testing:  # blocks CI otherwise
    app = make_wsgi_app()
    httpd = make_server('', conf.worker.metrics.port, app)
    httpd.serve_forever()
