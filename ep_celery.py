#! /usr/bin/env python
# -*- coding: utf-8 -*-
from wsgiref.simple_server import make_server

from celery import Celery
from prometheus_client import make_wsgi_app

from jarr.bootstrap import conf

celery_app = Celery(broker=conf.celery.BROKER_URL, config_source=conf.celery)

app = make_wsgi_app()
httpd = make_server('', conf.worker.metrics.port, app)
httpd.serve_forever()
