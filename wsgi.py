#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import request_finished

from jarr.bootstrap import conf, session
from jarr.api import create_app

application = create_app()


@request_finished.connect
def flush_on_finish(*args, **kwargs):
    session.flush()
    session.commit()


if __name__ == '__main__':  # pragma: no cover
    application.run(host=conf.webserver.host,
                    port=conf.webserver.port,
                    debug=True)
