#!/usr/bin/python3
import sys
from datetime import timedelta
import math

from flask_script import Command, Option

from bootstrap import conf
from lib.utils import utc_now
from web.controllers import FeedController, ArticleController

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
        print("feeds.warning %d" % int(total / 5))
        print("feeds.critical %d" % int(total / 2))
        print("graph_category web")
        print("graph_scale yes")
        print("graph_args --logarithmic")

    def execute(self):
        fcontr = FeedController(ignore_context=True)

        print("feeds.value %d" % len(list(fcontr.list_late(limit=0))))
        print("feeds_total.value %d" % self._get_total_feed())


class FeedLatenessProbe(AbstractMuninPlugin):
    split_number = 12
    colour_expired = '3B0B17'
    colour_in_a_while = '2E2EFE'

    @staticmethod
    def colors(nb_steps):
        red, green, blue = 255, 0, 0
        steps = 255 * 2 / (nb_steps - 1)
        yield '{:02X}{:02X}{:02X}'.format(red, green, blue)
        for _ in range(nb_steps):
            if green < 255:
                green += steps
                if green > 255:
                    red -= green - 255
                    green = 255
            else:
                red -= steps
            yield '{:02X}{:02X}{:02X}'.format(int(red if red < 255 else 255),
                int(green if green > 0 else 0), int(blue))

    def iter_on_splits(self):
        offset = 2
        min_delta = timedelta(0)
        power = math.log(conf.FEED_MAX_EXPIRES, self.split_number + offset)
        yield 'before', None, min_delta
        for i in range(offset, self.split_number + offset):
            if i != offset:
                range_start = timedelta(seconds=pow(i, power))
            else:
                range_start = timedelta(0)
            yield i - offset, range_start, timedelta(seconds=pow(i + 1, power))
        yield 'late', timedelta(seconds=conf.FEED_MAX_EXPIRES), None

    @staticmethod
    def _to_hour(td):
        time, total_minutes = "", td.total_seconds() / 60
        hour, minutes = int(total_minutes / 60), total_minutes % 60
        if hour:
            time += "%dh" % hour
        if minutes:
            time += ("%02dm" if time else "%dm") % minutes
        return time or "now"

    def config(self):
        print("graph_title JARR - Feeds lateness repartition")
        print("graph_vlabel feeds counts")
        colors = self.colors(self.split_number)
        for i, range_start, range_end in self.iter_on_splits():
            print("feeds_%s.draw AREASTACK" % i)
            print("feeds_%s.min 0" % i)
            if i == 'before':
                print("feeds_before.colour %s" % self.colour_expired)
                print("feeds_before.label %s" % 'feeds expired')
                print("feeds_before.info feeds already expired (%s)"
                      % self._to_hour(range_end))
            elif i == 'late':
                print("feeds_late.colour %s" % self.colour_in_a_while)
                print("feeds_late.label %s" % 'feeds expiring after max limit')
                print("feeds_late.info feeds that will expire in more "
                      "than %s" % self._to_hour(range_start))

            else:
                print("feeds_%s.colour %s" % (i, next(colors)))
                print("feeds_%s.label feeds in split %d" % (i, i))
                print("feeds_%s.info feeds expiring in between %s and %s" % (i,
                      self._to_hour(range_start), self._to_hour(range_end)))

        print("graph_category web")
        print("graph_scale no")

    def execute(self):
        fctrl = FeedController(ignore_context=True)
        now = utc_now()
        for i, range_start, range_end in self.iter_on_splits():
            filters = {}
            if range_start is not None:
                filters['expires__ge'] = now + range_start
            if range_end is not None:
                filters['expires__lt'] = now + range_end
            print("feeds_%s.value %d"
                  % (i, fctrl.get_active_feed(**filters).count()))


class ArticleProbe(AbstractMuninPlugin):

    def config(self):
        print("graph_title JARR - Articles adding rate")
        print("graph_vlabel Articles per sec")
        print("articles.label Overall rate")
        print("articles.type DERIVE")
        print("articles.min 0")
        fcontr = FeedController(ignore_context=True)
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
