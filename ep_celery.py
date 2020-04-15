#! /usr/bin/env python
# -*- coding: utf-8 -*-
from celery import Celery, signals
from jarr.bootstrap import conf, commit_pending_sql, rollback_pending_sql

celery_app = Celery(broker=conf.celery.BROKER_URL, config_source=conf.celery)
signals.task_success.connect(commit_pending_sql)
signals.task_failure.connect(rollback_pending_sql)
