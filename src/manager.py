#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bootstrap import application, db, populate_g, conf
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from web.controllers.user import UserController

import web.models

Migrate(application, db)

manager = Manager(application)
manager.add_command('db', MigrateCommand)


@manager.command
def db_empty():
    "Will drop every datas stocked in db."
    with application.app_context():
        populate_g()
        web.models.db_empty(db)


@manager.command
def db_create(admin=None):
    "Will create the database from conf parameters."
    if not admin:
        admin = {}
    if 'login' not in admin:
        admin['login'] = 'admin'
    if 'password' not in admin:
        admin['password'] = 'admin'
    admin.update({'is_admin': True})
    with application.app_context():
        populate_g()
        db.create_all()
        UserController().create(**admin)


@manager.command
def fetch(limit=100, retreive_all=False):
    "Crawl the feeds with the client crawler."
    from crawler.http_crawler import CrawlerScheduler
    scheduler = CrawlerScheduler(conf.API_LOGIN, conf.API_PASSWD)
    scheduler.run(limit=limit, retreive_all=retreive_all)
    scheduler.wait()


@manager.command
def fetch_asyncio(user_id, feed_id):
    "Crawl the feeds with asyncio."
    import asyncio

    with application.app_context():
        populate_g()
        from flask import g
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
            if user.activation_key == "":
                print("Fetching articles for " + user.login)
                g.user = user
                classic_crawler.retrieve_feed(loop, g.user, feed_id)
        loop.close()

from scripts.probes import ArticleProbe, FeedProbe
manager.add_command('probe_articles', ArticleProbe())
manager.add_command('probe_feeds', FeedProbe())

if __name__ == '__main__':
    manager.run()
