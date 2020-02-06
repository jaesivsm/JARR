#! /usr/bin/env python
# -*- coding: utf-8 -*-
from celery import Celery
from jarr.bootstrap import conf

celery_app = Celery(broker=conf.celery.BROKER_URL, config_source=conf.celery)
