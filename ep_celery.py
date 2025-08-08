#! /usr/bin/env python
# -*- coding: utf-8 -*-
from celery import Celery, signals

from jarr.bootstrap import commit_pending_sql, conf, rollback_pending_sql
from prometheus_client import (
    CollectorRegistry,
    multiprocess,
    start_http_server,
)


@signals.celeryd_init.connect
def start_metrics_server(_sender=None, _conf=None, **_kwargs):  # type: ignore
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)

    start_http_server(9100, registry=registry)


@signals.worker_process_shutdown.connect
def handle_shutdown(*args, pid=None, **kwargs):
    if pid:
        multiprocess.mark_process_dead(pid)


signals.task_success.connect(commit_pending_sql)
signals.task_failure.connect(rollback_pending_sql)
celery_app = Celery(broker=conf.celery.broker_url, config_source=conf.celery)
