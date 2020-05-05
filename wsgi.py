#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from jarr.bootstrap import conf
from jarr.api import create_app

application = create_app()


if __name__ == '__main__':  # pragma: no cover
    application.run(host=conf.api.addr, port=conf.api.port,
                    debug=conf.log.level <= logging.DEBUG)
