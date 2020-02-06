#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta, timezone

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from jarr.lib.utils import utc_now

from jarr.bootstrap import conf, Base
from jarr.scripts.probes import ArticleProbe, FeedProbe, FeedLatenessProbe
from jarr.controllers import FeedController, UserController

from wsgi import application

logger = logging.getLogger(__name__)
Migrate(application, Base)
manager = Manager(application)
manager.add_command('db', MigrateCommand)


@manager.command
def db_create(login='admin', password='admin'):
    "Will create the database from conf parameters."
    admin = {'is_admin': True, 'is_api': True,
             'login': login, 'password': password}
    with application.app_context():
        Base.metadata.create_all()
        UserController(ignore_context=True).create(**admin)


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


manager.add_command('probe_articles', ArticleProbe())
manager.add_command('probe_feeds', FeedProbe())
manager.add_command('probe_feeds_lateness', FeedLatenessProbe())

if __name__ == '__main__':  # pragma: no cover
    manager.run()
