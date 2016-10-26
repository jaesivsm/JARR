#!/usr/bin/python3
import sys
from datetime import datetime, timedelta

from flask_script import Command, Option

from bootstrap import conf
from web.controllers import FeedController, ArticleController
from web.models import User

DEFAULT_HEADERS = {'Content-Type': 'application/json', 'User-Agent': 'munin'}


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
        return FeedController(ignore_context=True).get_active_feed().count()

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
        delta = timedelta(minutes=conf.FEED_REFRESH_RATE)
        fcontr = FeedController(ignore_context=True)

        print("feeds.value %d" % len(list(fcontr.list_late(delta, limit=0))))
        print("feeds_total.value %d" % self._get_total_feed())


class FeedLatenessProbe(AbstractMuninPlugin):
    split_number = 6
    colours = ['05FF0B', '99FD03', 'E6FC02', 'FCC402', 'FB7601', 'F90026']
    colour_after = '3B0B17'
    colour_before = '2E2EFE'

    def _get_feeds(self):
        last_conn_max = datetime.utcnow() - timedelta(days=30)
        return list(FeedController(ignore_context=True).get_active_feed())

    def iter_on_splits(self):
        delta = timedelta(minutes=conf.FEED_REFRESH_RATE)
        split_delta = delta / self.split_number
        yield 'before', timedelta(0), None
        for i in range(self.split_number):
            range_start = split_delta * (i + 1)
            range_end = split_delta * i
            yield i, range_start, range_end
        yield 'late', None, delta

    def config(self):
        print("graph_title JARR - Feeds lateness repartition")
        print("graph_vlabel feeds counts")
        colours = iter(self.colours)
        for i, range_start, range_end in self.iter_on_splits():
            print("feeds_%s.draw AREASTACK" % i)
            print("feeds_%s.min 0" % i)
            if i == 'before':
                print("feeds_before.colour %s" % self.colour_before)
                print("feeds_before.label %s" % 'feeds early')
                print("feeds_before.info %s"
                        % 'feeds with fetch date in the future')
            elif i == 'late':
                print("feeds_late.colour %s" % self.colour_after)
                print("feeds_late.label %s" % 'late feed')
                print("feeds_late.info feed fetched more than %d minutes ago"
                        % (range_end.seconds / 60))
            else:
                print("feeds_%s.colour %s" % (i, next(colours)))
                print("feeds_%s.label feeds in split %d" % (i, i))
                print("feeds_%s.info feeds fetched between %d "
                      "and %d minutes ago" % (i,
                          range_end.seconds / 60, range_start.seconds / 60))
        print("graph_category web")
        print("graph_scale no")

    def execute(self):
        feeds = self._get_feeds()
        now = datetime.utcnow()
        for i, range_start, range_end in self.iter_on_splits():
            count = 0
            for fd in feeds:
                if range_start is None:
                    if fd.last_retrieved <= now - range_end:
                        count += 1
                elif range_end is None:
                    if now - range_start < fd.last_retrieved:
                        count += 1
                elif now - range_start < fd.last_retrieved <= now - range_end:
                    count += 1
            print("feeds_%s.value %d" % (i, count))


class ArticleProbe(AbstractMuninPlugin):

    def config(self):
        print("graph_title JARR - Articles adding rate")
        print("graph_vlabel Articles per sec")
        print("articles.label Overall rate")
        print("articles.type DERIVE")
        print("articles.min 0")
        fcontr = FeedController(ignore_context=True)
        last_conn_max = datetime.utcnow() - timedelta(days=30)
        for id_ in fcontr.get_active_feed()\
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
