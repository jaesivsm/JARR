#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta, timezone

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from jarr.api import create_app
from jarr.bootstrap import Base, conf
from jarr.controllers import FeedController, UserController
from jarr.lib.utils import utc_now

application = create_app()

logger = logging.getLogger(__name__)
Migrate(application, Base)
manager = Manager(application)
manager.add_command('db', MigrateCommand)


@manager.command
def db_create(login='admin', password='admin'):
    """Will create the database from conf parameters."""
    admin = {'is_admin': True, 'is_api': True,
             'login': login, 'password': password}
    Base.metadata.create_all()
    UserController().create(**admin)


@manager.command
def reset_feeds():
    """Will reschedule all active feeds to be fetched in the next two hours"""
    fcontr = FeedController(ignore_context=True)
    now = utc_now()
    feeds = [feed[0] for feed in fcontr.get_active_feed()
                                       .with_entities(fcontr._db_cls.id)]

    step = timedelta(seconds=conf.feed.max_expires / len(feeds))
    for i, feed_id in enumerate(feeds):
        fcontr.update({'id': feed_id},
                {'etag': '', 'last_modified': '',
                 'last_retrieved': datetime(1970, 1, 1, tzinfo=timezone.utc),
                 'expires': now + i * step})


if __name__ == '__main__':  # pragma: no cover
    manager.run()
