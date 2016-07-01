import logging
import itertools
from datetime import datetime, timedelta

import conf
from .abstract import AbstractController
from .icon import IconController
from web.models import User, Feed
from web.lib.utils import clear_string

logger = logging.getLogger(__name__)
DEFAULT_LIMIT = 5


class FeedController(AbstractController):
    _db_cls = Feed

    def __get_art_contr(self):
        from .article import ArticleController
        return ArticleController(self.user_id)

    def list_late(self, delta, max_error=conf.FEED_ERROR_MAX,
                  limit=DEFAULT_LIMIT):
        """Will list either late feed (which have been retrieved for the last
        time sooner than now minus the delta (default to 1h)) or the feed with
        articles recentrly created (later than now minus a quarter the delta
        (default to 15 logically)).

        The idea is to keep very active feed up to date and to avoid missing
        articles du to high activity (when, for example, the feed only displays
        its 30 last entries and produces more than one per minutes).
        """
        tenth = delta / 10
        feed_last_retrieved = datetime.utcnow() - delta
        art_last_retr = datetime.utcnow() - (2 * tenth)
        min_wait = datetime.utcnow() - tenth
        ac = self.__get_art_contr()
        new_art_feed = (ac.read(retrieved_date__gt=art_last_retr,
                                retrieved_date__lt=min_wait)
                          .with_entities(ac._db_cls.feed_id)
                          .distinct())

        query = (self.read(error_count__lt=max_error, enabled=True,
                           __or__=[{'last_retrieved__lt': feed_last_retrieved},
                                   {'last_retrieved__lt': min_wait,
                                    'id__in': new_art_feed}])
                     .join(User).filter(User.is_active == True)
                     .order_by(Feed.last_retrieved))
        if limit:
            query = query.limit(limit)
        yield from query

    def list_fetchable(self, max_error=conf.FEED_ERROR_MAX,
            limit=DEFAULT_LIMIT, refresh_rate=conf.FEED_REFRESH_RATE):
        now, delta = datetime.utcnow(), timedelta(minutes=refresh_rate)
        feeds = list(self.list_late(delta, max_error, limit))
        if feeds:
            self.update({'id__in': [feed.id for feed in feeds]},
                        {'last_retrieved': now})
        return feeds

    def get_duplicates(self, feed_id):
        """
        Compare a list of documents by pair.
        Pairs of duplicates are sorted by "retrieved date".
        """
        feed = self.get(id=feed_id)
        duplicates = []
        for pair in itertools.combinations(feed.articles, 2):
            date1, date2 = pair[0].date, pair[1].date
            if clear_string(pair[0].title) == clear_string(pair[1].title) \
                    and (date1 - date2) < timedelta(days=1):
                if pair[0].retrieved_date < pair[1].retrieved_date:
                    duplicates.append((pair[0], pair[1]))
                else:
                    duplicates.append((pair[1], pair[0]))
        return feed, duplicates

    def get_inactives(self, nb_days):
        today = datetime.utcnow()
        inactives = []
        for feed in self.read():
            try:
                last_post = feed.articles[0].date
            except IndexError:
                continue
            elapsed = today - last_post
            if elapsed > timedelta(days=nb_days):
                inactives.append((feed, elapsed))
        inactives.sort(key=lambda tup: tup[1], reverse=True)
        return inactives

    def count_by_category(self, **filters):
        return self._count_by(Feed.category_id, filters)

    def _ensure_icon(self, attrs):
        if not attrs.get('icon_url'):
            return
        icon_contr = IconController()
        if not icon_contr.read(url=attrs['icon_url']).count():
            icon_contr.create(**{'url': attrs['icon_url']})

    def create(self, **attrs):
        self._ensure_icon(attrs)
        return super().create(**attrs)

    def update(self, filters, attrs):
        self._ensure_icon(attrs)
        if 'category_id' in attrs:
            if attrs['category_id'] == 0:
                attrs['category_id'] = None
            for feed in self.read(**filters):
                self.__get_art_contr().update({'feed_id': feed.id},
                        {'category_id': attrs['category_id']})
        return super().update(filters, attrs)
