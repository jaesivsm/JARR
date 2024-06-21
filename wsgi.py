#! /usr/bin/env python
# -*- coding: utf-8 -*-
import click
from werkzeug.middleware.proxy_fix import ProxyFix

from jarr.api import create_app
from jarr.bootstrap import sqlalchemy_registry, engine, Base
from flask_migrate import Migrate


_app = create_app()
application = ProxyFix(_app, x_for=1, x_proto=1, x_host=1, x_port=1)
migrate = Migrate(db=Base)
migrate.init_app(_app)


@_app.cli.command("bootstrap-database")
@click.option("--admin_login", default="admin")
@click.option("--admin_password", default="admin")
def bootstrap_database(admin_login, admin_password):
    """Will create the database from conf parameters."""
    sqlalchemy_registry.configure()
    from jarr.controllers.user import UserController
    admin = {'is_admin': True, 'is_api': True,
             'login': admin_login, 'password': admin_password}
    Base.metadata.create_all(engine)
    UserController().create(**admin)
