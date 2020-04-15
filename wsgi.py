#! /usr/bin/env python
# -*- coding: utf-8 -*-
from jarr.bootstrap import conf
from jarr.api import create_app

application = create_app()


if __name__ == '__main__':  # pragma: no cover
    application.run(host=conf.webserver.host,
                    port=conf.webserver.port,
                    debug=True)
