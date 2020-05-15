#! /usr/bin/env python
# -*- coding: utf-8 -*-
from werkzeug.middleware.proxy_fix import ProxyFix
from jarr.api import create_app

application = ProxyFix(create_app(), x_for=1, x_proto=1, x_host=1, x_port=1)
