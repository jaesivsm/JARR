import logging
from collections import OrderedDict, defaultdict
from datetime import datetime, timedelta

import dateutil.parser
from sqlalchemy import and_
from sqlalchemy.sql import delete, select, update
from werkzeug.exceptions import Forbidden

from jarr.bootstrap import conf, session
from jarr.controllers.abstract import AbstractController
from jarr.controllers.icon import IconController
from jarr.lib.enums import FeedStatus
from jarr.lib.utils import utc_now
from jarr.models import Article, Category, Cluster, Feed, User

DEFAULT_LIMIT = 0
DEFAULT_ART_SPAN_TIME = timedelta(seconds=conf.feed.max_expires)
logger = logging.getLogger(__name__)
LIST_W_CATEG_MAPPING = OrderedDict((('id', Feed.id),
                                    ('str', Feed.title),
                                    ('icon_url', Feed.icon_url),
                                    ('category_id', Feed.category_id),
                                    ('last_retrieved', Feed.last_retrieved),
                                    ('error_count', Feed.error_count),
                                    ('last_error', Feed.last_error),
                                    ))


class FeedController(AbstractController):
    _db_cls = Feed

    @property
    def __actrl(self):
        from .article import ArticleController
        return ArticleController(self.user_id)

    def list_w_categ(self):
        feeds = defaultdict(list)
        for row in session.query(*LIST_W_CATEG_MAPPING.values())\
                .filter(Feed.user_id == self.user_id,
                        Feed.status != FeedStatus.to_delete,
                        Feed.status != FeedStatus.deleting)\
                .order_by(Feed.title):
            row = dict(zip(LIST_W_CATEG_MAPPING, row))
            row['type'] = 'feed'
            feeds[row['category_id']].append(row)
        yield {'id': None, 'str': None, 'type': 'all-categ'}
        yield from feeds.get(None, [])
        for cid, cname in session.query(Category.id, Category.name)\
                    .filter(Category.user_id == self.user_id)\
                    .order_by(Category.name.nullsfirst()):
            yield {'id': cid, 'str': cname, 'type': 'categ'}
            yield from feeds.get(cid, [])

    def get_active_feed(self, **filters):
        filters['error_count__lt'] = conf.feed.error_max
        query = self.read(status=FeedStatus.active, **filters)
        last_conn = utc_now() - timedelta(days=conf.feed.stop_fetch)
        if conf.feed.stop_fetch:
            return query.join(User).filter(User.is_active.__eq__(True),
                                           User.last_connection >= last_conn)
        return query

    def list_late(self, limit=DEFAULT_LIMIT):
        """Will list either late feeds or feeds with articles recently created.

        Late feeds are feeds which have been retrieved for the last time sooner
        than now minus the delta (default to 1h). The others are feeds with
        article created later than now minus a quarter the delta (default to
        15 logically).

        The idea is to keep very active feed up to date and to avoid missing
        articles du to high activity (when, for example, the feed only displays
        its 30 last entries and produces more than one per minutes).

        Feeds of inactive (not connected for more than a month) or manually
        desactivated users are ignored.
        """
        now = utc_now()
        max_ex = now + timedelta(seconds=conf.feed.max_expires)
        min_delta = timedelta(seconds=conf.feed.min_expires)
        query = self.get_active_feed().filter(
                *(self._to_filters(
                    __or__=[{'last_retrieved__lt': now - min_delta},
                            {'last_retrieved__gt': now + min_delta}])
                .union(self._to_filters(
                    __or__=[{'expires__lt': now},
                            {'expires__gt': max_ex}])))).order_by(Feed.expires)
        if limit:
            query = query.limit(limit)
        yield from query

    def list_fetchable(self, limit=DEFAULT_LIMIT):
        now, feeds = utc_now(), list(self.list_late(limit))
        if feeds:
            self.update({'id__in': [feed.id for feed in feeds]},
                        {'last_retrieved': now})
        return feeds

    @staticmethod
    def _ensure_icon(attrs):
        if not attrs.get('icon_url'):
            return
        icon_contr = IconController()
        if not icon_contr.read(url=attrs['icon_url']).first():
            icon_contr.create(url=attrs['icon_url'])

    def __clean_feed_fields(self, attrs):
        if attrs.get('category_id') == 0:
            attrs['category_id'] = None
        if self.user_id and attrs.get('category_id'):
            from jarr.controllers import CategoryController
            category = CategoryController().get(id=attrs['category_id'])
            if category.user_id != self.user_id:
                raise Forbidden()
        if 'filters' in attrs:
            attrs['filters'] = [filter_ for filter_ in (attrs['filters'] or [])
                                if isinstance(filter_, dict)]

    def create(self, **attrs):
        self._ensure_icon(attrs)
        self.__clean_feed_fields(attrs)
        return super().create(**attrs)

    def __denorm_cat_id_on_articles(self, feed, attrs):
        if 'category_id' in attrs:
            self.__actrl.update({'feed_id': feed.id},
                    {'category_id': attrs['category_id']})

    def __denorm_title_on_clusters(self, feed, attrs):
        if 'title' in attrs:
            if self.user_id:
                where_clause = and_(Article.user_id == self.user_id,
                                    Article.feed_id == feed.id)
            else:
                where_clause = Article.feed_id == feed.id
            stmt = update(Cluster)\
                    .where(and_(Article.id == Cluster.main_article_id,
                                where_clause))\
                    .values(dict(main_feed_title=attrs['title']))
            session.execute(stmt)

    def __update_default_expires(self, feed, attrs):
        now = utc_now()
        expires = []
        if attrs['expires']:
            if not isinstance(attrs['expires'], datetime):
                expires.append(dateutil.parser.parse(attrs['expires']))
            else:
                expires.append(attrs['expires'])

        span_time = timedelta(seconds=conf.feed.max_expires)
        art_count = self.__actrl.read(feed_id=feed.id,
                retrieved_date__gt=now - span_time).count()
        expires.append(now + (span_time / (art_count or 1)))
        attrs['expires'] = min(expires)
        logger.info('saw %d articles in the past %r seconds, expiring at %r',
                    art_count, span_time, attrs['expires'])

    def update(self, filters, attrs, return_objs=False, commit=True):
        self._ensure_icon(attrs)
        self.__clean_feed_fields(attrs)
        stuff_to_denorm = bool({'title', 'category_id'}.intersection(attrs))
        updating_expires = 'expires' in attrs

        if stuff_to_denorm or updating_expires:
            for feed in self.read(**filters):
                if stuff_to_denorm:
                    self.__denorm_cat_id_on_articles(feed, attrs)
                    self.__denorm_title_on_clusters(feed, attrs)
                if updating_expires:
                    self.__update_default_expires(feed, attrs)
        return super().update(filters, attrs, return_objs, commit)

    def delete(self, obj_id, commit=True):
        from jarr.controllers.cluster import ClusterController
        feed = self.get(id=obj_id)
        logger.debug('DELETE %r - Found feed', feed)
        clu_ctrl = ClusterController(self.user_id)

        logger.info('DELETE %r - removing back ref from cluster to article',
                    feed)
        clu_ctrl.update({'user_id': feed.user_id,
                         'main_article_id__in': self.__actrl.read(
                                feed_id=obj_id).with_entities('id')},
                        {'main_article_id': None})

        def select_art(col):
            return select([col]).where(and_(Cluster.id == Article.cluster_id,
                                            Article.user_id == feed.user_id))\
                                .order_by(Article.date.asc()).limit(1)

        logger.info('DELETE %r - removing articles', feed)
        session.execute(delete(Article).where(
                and_(Article.feed_id == feed.id,
                     Article.user_id == feed.user_id)))

        logger.info('DELETE %r - fixing cluster without main article', feed)
        clu_ctrl.update({'user_id': feed.user_id, 'main_article_id': None},
                {'main_title': select_art(Article.title),
                 'main_article_id': select_art(Article.id),
                 'main_feed_title': select([Feed.title])
                                    .where(and_(
                                           Cluster.id == Article.cluster_id,
                                           Article.user_id == feed.user_id,
                                           Feed.id == Article.feed_id,
                                           Feed.user_id == feed.user_id))
                                    .order_by(Article.date.asc()).limit(1)})

        logger.info('DELETE %r - removing clusters without main article', feed)
        session.execute(delete(Cluster).where(
                and_(Cluster.user_id == feed.user_id,
                     Cluster.main_article_id.__eq__(None))))
        return super().delete(obj_id)

    def get_crawler(self, feed_id):
        from jarr.crawler.crawlers import AbstractCrawler, ClassicCrawler
        feed = self.get(id=feed_id)
        crawlers = set(AbstractCrawler.__subclasses__()).union(
                ClassicCrawler.__subclasses__())
        for crawler in crawlers:
            if feed.feed_type is crawler.feed_type:
                return crawler(feed)
        raise ValueError('No crawler for %r' % feed.feed_type)
