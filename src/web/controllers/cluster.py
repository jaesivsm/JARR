import logging
from bootstrap import conf, db

from sqlalchemy import func, Integer, or_, and_
from sqlalchemy.sql import select, exists
from sqlalchemy.dialects.postgres import ARRAY
from werkzeug.exceptions import NotFound
from .abstract import AbstractController
from web.models import Cluster, Article
from web.models.relationships import cluster_as_feed, cluster_as_category
from web.controllers.article import ArticleController

logger = logging.getLogger(__name__)


class ClusterController(AbstractController):
    _db_cls = Cluster

    def _get_cluster_by_link(self, article):
        return self.read(user_id=article.user_id,
                         main_link=article.link).first()

    def _get_cluster_by_title(self, article):
        if article.category and article.category.cluster_on_title:
            try:
                article = ArticleController(self.user_id).get(
                        user_id=article.user_id,
                        category_id=article.category_id,
                        title__ilike=article.title)
            except NotFound:
                return
            return article.cluster

    def _create_from_article(self, article,
                             cluster_read=None, cluster_liked=False):
        cluster = Cluster()
        cluster.user_id = article.user_id
        cluster.main_link = article.link
        cluster.main_date = article.date
        cluster.main_feed_title = article.feed.title
        cluster.main_title = article.title
        cluster.main_article_id = article.id
        cluster.read = bool(cluster_read)
        cluster.liked = cluster_liked
        self._enrich_cluster(cluster, article, cluster_read, cluster_liked)

    def _enrich_cluster(self, cluster, article,
                        cluster_read=None, cluster_liked=False):
        article.cluster = cluster
        # a cluster
        if cluster_read is not None:
            cluster.read = cluster.read and cluster_read
        # once one article is liked the cluster is liked
        cluster.liked = cluster.liked or cluster_liked
        if cluster.main_date > article.date:
            cluster.main_title = article.title
            cluster.main_date = article.date
            cluster.main_feed_title = article.feed.title
            cluster.main_article_id = article.id
        cluster.feeds.append(article.feed)
        if article.category_id:
            cluster.categories.append(article.category)
        db.session.add(cluster)
        db.session.add(article)
        db.session.commit()

    def clusterize(self, article, cluster_read=None, cluster_liked=False):
        """Will add given article to a fitting cluster or create a cluster
        fitting that article."""
        cluster = self._get_cluster_by_link(article)
        if not cluster:
            cluster = self._get_cluster_by_title(article)
        if cluster:
            return self._enrich_cluster(cluster, article,
                                        cluster_read, cluster_liked)
        return self._create_from_article(article, cluster_read, cluster_liked)

    def join_read(self, feed_id=None, category_id=None, **filters):
        art_filters = {}
        if self.user_id:
            filters['user_id'] = self.user_id

        for key in {'__or__', 'title__ilike', 'content__ilike'}\
                   .intersection(filters):
            art_filters[key] = filters.pop(key)

        if art_filters:
            art_contr = ArticleController(self.user_id)
            filters['id__in'] = {line[0] for line in art_contr
                    .read(**art_filters).with_entities(Article.cluster_id)}

            if not filters['id__in']:
                return

        caf_cols = cluster_as_feed.columns
        cac_cols = cluster_as_category.columns
        fields = {key: getattr(Cluster, key) for key in ('main_title', 'id',
                  'liked', 'read', 'main_article_id', 'main_feed_title',
                  'main_date', 'main_link')}
        sqla_fields = list(fields.values())
        selected_fields = list(fields.values())

        if 'sqlite' in conf.SQLALCHEMY_DATABASE_URI:
            selected_fields.append(
                    func.group_concat(caf_cols['feed_id']).label('feeds_id'))
            if category_id:
                selected_fields.append(func.group_concat(
                        cac_cols['category_id']).label('categories_id'))
        else:
            selected_fields.append(func.array_agg(caf_cols['feed_id'],
                    type_=ARRAY(Integer)).label('feeds_id'))
            if category_id:
                selected_fields.append(func.array_agg(cac_cols['category_id'],
                        type_=ARRAY(Integer)).label('categories_id'))

        # DESC of what's going on below :
        # base query with the above fields and the aggregations
        query = db.session.query(*selected_fields)

        # adding parent filter, but we can't just filter on one id, because
        # we'll miss all the other parent of the cluster
        if feed_id:
            cluster_has_feed = exists(select([caf_cols['feed_id']])
                    .where(and_(caf_cols['cluster_id'] == Cluster.id,
                                caf_cols['feed_id'] == feed_id))
                    .correlate(Cluster))
            query = query.join(cluster_as_feed,
                               caf_cols['cluster_id'] == Cluster.id)\
                         .filter(cluster_has_feed)
        else:
            query = query.join(cluster_as_feed,
                    caf_cols['cluster_id'] == Cluster.id)
        if category_id:
            # joining only if filtering on categories to lighten the query
            # as every article doesn't obligatorily have a category > outerjoin
            cluster_has_category = exists(select([cac_cols['category_id']])
                    .where(and_(cac_cols['cluster_id'] == Cluster.id,
                                cac_cols['category_id'] == category_id))
                    .correlate(Cluster))
            query = query.join(cluster_as_category,
                               cac_cols['cluster_id'] == Cluster.id)\
                         .filter(cluster_has_category)

        # applying common filter (read / liked)
        # grouping all the fields so that agreg works on distant ids
        query = query.group_by(*sqla_fields)\
                     .filter(*self._to_filters(**filters))

        for clu in query.order_by(Cluster.main_date.desc()).limit(1000):
            row = {}
            for key in fields:
                row[key] = getattr(clu, key)
            if 'sqlite' in conf.SQLALCHEMY_DATABASE_URI:
                row['feeds_id'] = set(map(int, clu.feeds_id.split(',')))
                if category_id and clu.categories_id:
                    row['categories_id'] = set(
                            map(int, clu.categories_id.split(',')))
                elif category_id:
                    row['categories_id'] = [0]
            else:
                row['feeds_id'] = set(clu.feeds_id)
                if category_id:
                    row['categories_id'] = set(clu.categories_id)
            yield row

    @classmethod
    def _extra_columns(cls, role, right):
        return {'articles': {'type': list}}

    def count_by_feed(self, **filters):
        return self._count_by(cluster_as_feed.columns['feed_id'], **filters)

    def count_by_category(self, **filters):
        return self._count_by(cluster_as_category.columns['category_id'],
                              **filters)

    def _count_by(self, group_on, **filters):
        if self.user_id:
            filters['user_id'] = self.user_id
        return dict(db.session.query(group_on, func.count('cluster_id'))
                              .outerjoin(Cluster)
                              .filter(*self._to_filters(**filters))
                              .group_by(group_on).all())
