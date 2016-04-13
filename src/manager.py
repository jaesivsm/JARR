#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from bootstrap import application, db, conf
import web.models
from web.controllers import FeedController, UserController
from scripts.probes import ArticleProbe, FeedProbe

logger = logging.getLogger(__name__)
Migrate(application, db)
manager = Manager(application)
manager.add_command('db', MigrateCommand)


@manager.command
def db_empty():
    "Will drop every datas stocked in db."
    with application.app_context():
        web.models.db_empty(db)


@manager.command
def db_create(login='admin', password='admin'):
    "Will create the database from conf parameters."
    admin = {'is_admin': True, 'is_api': True,
             'login': login, 'password': password}
    with application.app_context():
        db.create_all()
        UserController(ignore_context=True).create(**admin)


@manager.command
def fetch(limit=100, retreive_all=False):
    "Crawl the feeds with the client crawler."
    from crawler.http_crawler import CrawlerScheduler
    scheduler = CrawlerScheduler(conf.CRAWLER_LOGIN, conf.CRAWLER_PASSWD)
    scheduler.run(limit=limit, retreive_all=retreive_all)
    scheduler.wait()


@manager.command
def reset_feeds():
    contr = FeedController()
    step = timedelta(seconds=3600 / contr.read().count())
    now = datetime.utcnow()
    for i, feed in enumerate(contr.read()
            .order_by(contr._db_cls.last_retrieved)):
        contr.update({'id': feed.id},
                {'etag': '', 'last_modified': '',
                 'last_retrieved': now - i * step})


@manager.command
def fetch_asyncio(user_id, feed_id):
    "Crawl the feeds with asyncio."
    import asyncio

    with application.app_context():
        from flask.ext.login import current_user
        from crawler import classic_crawler
        ucontr = UserController()
        users = []
        try:
            users = [ucontr.get(user_id)]
        except:
            users = ucontr.read()
        finally:
            if users == []:
                users = ucontr.read()

        try:
            feed_id = int(feed_id)
        except:
            feed_id = None

        loop = asyncio.get_event_loop()
        for user in users:
            if user.is_active:
                logger.warn("Fetching articles for " + user.login)
                classic_crawler.retrieve_feed(loop, current_user, feed_id)
        loop.close()


manager.add_command('probe_articles', ArticleProbe())
manager.add_command('probe_feeds', FeedProbe())

if __name__ == '__main__':  # pragma: no cover
    manager.run()
