#! /usr/bin/env python
# -*- coding: utf-8 -*-
import click
from werkzeug.middleware.proxy_fix import ProxyFix

from jarr.api import create_app
from jarr.bootstrap import Base
from flask_migrate import Migrate, MigrateCommand


_app = create_app()
application = ProxyFix(_app, x_for=1, x_proto=1, x_host=1, x_port=1)
migrate = Migrate(application, Base)


@_app.cli.command("bootstrap-database")
@click.option("--login", default="admin")
@click.option("--password", default="admin")
def bootstrap_database(login, password):
    """Will create the database from conf parameters."""
    from jarr.controllers.user import UserController
    admin = {'is_admin': True, 'is_api': True,
             'login': login, 'password': password}
    Base.metadata.create_all()
    UserController().create(**admin)
