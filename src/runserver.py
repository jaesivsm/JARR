#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bootstrap import conf, create_app, load_blueprints, init_babel

application = create_app()

if conf.ON_HEROKU:
    from flask_sslify import SSLify
    SSLify(application)


init_babel(application)
load_blueprints(application)

if __name__ == '__main__':  # pragma: no cover
    application.run(host=conf.WEBSERVER_HOST,
                    port=conf.WEBSERVER_PORT,
                    debug=True)
