#!/usr/bin/python3
import sys
from datetime import datetime, timedelta

from flask_script import Command, Option

from web.controllers import ArticleController, FeedController
from web.models import User

DEFAULT_HEADERS = {'Content-Type': 'application/json', 'User-Agent': 'munin'}
LATE_AFTER = 60
FETCH_RATE = 3


class AbstractMuninPlugin(Command):
    urn = None

    def execute(self):
        raise NotImplementedError()

    def config(self):
        raise NotImplementedError()

    def get_options(self):
        if sys.argv[-1] == 'config':
            return [Option(dest='config', default=sys.argv[-1] == 'config')]
        return []

    def run(self, config=False):
        if config:
            self.config()
        else:
            self.execute()


class FeedProbe(AbstractMuninPlugin):

    def _get_total_feed(self):
        last_conn_max = datetime.utcnow() - timedelta(days=30)
        return FeedController(ignore_context=True).read()\
                     .join(User).filter(User.is_active.__eq__(True),
                                        User.last_connection >= last_conn_max)\
                     .count()

    def config(self):
        total = self._get_total_feed()
        print("graph_title JARR - Feeds counts")
        print("graph_vlabel feeds")
        print("feeds.label Late feeds")
        print("feeds_total.label Total feeds")
        print("feeds.warning %d" % int(total / 20))
        print("feeds.critical %d" % int(total / 10))
        print("graph_category web")
        print("graph_scale yes")
        print("graph_args --logarithmic")

    def execute(self):
        delta = timedelta(minutes=LATE_AFTER + FETCH_RATE + 1)
        fcontr = FeedController(ignore_context=True)

        print("feeds.value %d" % len(list(fcontr.list_late(delta, limit=0))))
        print("feeds_total.value %d" % self._get_total_feed())


class ArticleProbe(AbstractMuninPlugin):

    def config(self):
        print("graph_title JARR - Articles adding rate")
        print("graph_vlabel Articles per sec")
        print("articles.label Overall rate")
        print("articles.type DERIVE")
        print("articles.min 0")
        fcontr = FeedController(ignore_context=True)
        last_conn_max = datetime.utcnow() - timedelta(days=30)
        for id_ in fcontr.read()\
                     .join(User).filter(User.is_active.__eq__(True),
                                        User.last_connection >= last_conn_max)\
                     .with_entities(fcontr._db_cls.user_id)\
                     .distinct().order_by('feed_user_id'):
            id_ = id_[0]
            print("articles_user_%s.label Rate for user %s" % (id_, id_))
            print("articles_user_%s.type DERIVE" % id_)
            print("articles_user_%s.min 0" % id_)
        print("graph_category web")
        print("graph_scale yes")

    def execute(self):
        counts = ArticleController(ignore_context=True).count_by_user_id()
        print("articles.value %s" % sum(counts.values()))
        for user, count in counts.items():
            print("articles_user_%s.value %s" % (user, count))
