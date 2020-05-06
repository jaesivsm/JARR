#! /usr/bin/env python
# -*- coding: utf-8 -*-
from celery import Celery, signals

from jarr.bootstrap import commit_pending_sql, conf, rollback_pending_sql

celery_app = Celery(broker=conf.celery.broker_url,
                    config_source=conf.celery)
signals.task_success.connect(commit_pending_sql)
signals.task_failure.connect(rollback_pending_sql)
