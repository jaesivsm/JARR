import logging
from datetime import timedelta

from sqlalchemy import Integer, and_, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import aliased
from sqlalchemy.sql import exists, select

from jarr_common.filter import process_filters
from jarr_common.reasons import ClusterReason, ReadReason
from jarr_common.clustering_af.grouper import get_best_match_and_score

from jarr.bootstrap import SQLITE_ENGINE, session
from jarr.controllers.article import ArticleController
from jarr.models import Article, Cluster

from .abstract import AbstractController

logger = logging.getLogger(__name__)
# static values for join_read
__returned_keys = ('main_title', 'id', 'liked', 'read', 'main_article_id',
                   'main_feed_title', 'main_date', 'main_link')
JR_FIELDS = {key: getattr(Cluster, key) for key in __returned_keys}
JR_SQLA_FIELDS = [getattr(Cluster, key) for key in __returned_keys]
JR_LENGTH = 1000


class ClusterController(AbstractController):
    _db_cls = Cluster
    max_day_dist = timedelta(days=7)

    def _get_cluster_by_link(self, article):
        filters = {'user_id': article.user_id,
                   'main_date__lt': article.date + self.max_day_dist,
                   'main_date__gt': article.date - self.max_day_dist,
                   'main_link': article.link}

        cluster = self.read(**filters).first()
        if not cluster:
            return None
        if not article.feed.cluster_same_feed:
            for clustered_article in cluster.articles:
                if clustered_article.feed_id == article.feed_id:
                    return None
        article.cluster_reason = ClusterReason.link
        return cluster

    def _get_cluster_by_similarity(self, article, min_sample_size=10):
        if not article.lang:
            return None
        art_contr = ArticleController(self.user_id)

        filters = {'user_id': article.user_id,
                   'date__lt': article.date + self.max_day_dist,
                   'date__gt': article.date - self.max_day_dist,
                   # article isn't this one, and already in a cluster
                   'cluster_id__ne': None, 'id__ne': article.id,
                   # article is matchable
                   'valuable_tokens__ne': []}
        if article.feed.cluster_tfidf_same_cat:
            filters['category_id'] = article.category_id

        neighbors = list(art_contr.read(**filters))
        if len(neighbors) < min_sample_size:
            logger.info('only %d docs against %d required, no TFIDF for %r',
                        len(neighbors), min_sample_size, article)
            return None

        best_match, score = get_best_match_and_score(article, neighbors)
        if score > article.feed.cluster_tfidf_min_score:
            article.cluster_reason = ClusterReason.tf_idf
            article.cluster_score = int(score * 1000)
            article.cluster_tfidf_neighbor_size = len(neighbors)
            article.cluster_tfidf_with = best_match.id
            return best_match.cluster

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
        article.cluster_reason = ClusterReason.original
        self.enrich_cluster(cluster, article, cluster_read, cluster_liked)
        return cluster

    @staticmethod
    def enrich_cluster(cluster, article,
                       cluster_read=None, cluster_liked=False,
                       force_article_as_main=False):
        article.cluster = cluster
        # a cluster
        if cluster_read is not None:
            cluster.read = cluster.read and cluster_read
            if cluster.read:
                cluster.read_reason = ReadReason.filtered
        elif article.feed.cluster_wake_up:
            cluster.read = False
        # once one article is liked the cluster is liked
        cluster.liked = cluster.liked or cluster_liked
        if cluster.main_date > article.date or force_article_as_main:
            cluster.main_title = article.title
            cluster.main_date = article.date
            cluster.main_feed_title = article.feed.title
            cluster.main_article_id = article.id
        session.add(cluster)
        session.add(article)
        session.commit()
        return cluster

    def clusterize(self, article, cluster_read=None, cluster_liked=False):
        """Will add given article to a fitting cluster or create a cluster
        fitting that article."""
        if article.feed.cluster_enabled:
            cluster = self._get_cluster_by_link(article)
            if not cluster and article.feed.cluster_tfidf:
                cluster = self._get_cluster_by_similarity(article)
            if cluster:
                return self.enrich_cluster(cluster, article,
                                           cluster_read, cluster_liked)
        return self._create_from_article(article, cluster_read, cluster_liked)

    @classmethod
    def clusterize_pending_articles(cls):
        results = []
        for article in ArticleController().read(cluster_id=None):
            _, read, liked = process_filters(article.feed.filters,
                    {'tags': article.tags,
                     'title': article.title,
                     'link': article.link})
            result = cls(article.user_id).clusterize(article, read, liked).id
            results.append(result)
        return results

    #
    # UI listing methods below
    #

    def _preprocess_per_article_filters(self, filters):
        """Removing filters aimed at articles and transform them into filters
        for clusters"""
        art_filters = {}
        for key in {'__or__', 'title__ilike', 'content__ilike'}\
                   .intersection(filters):
            art_filters[key] = filters.pop(key)

        if art_filters:
            art_contr = ArticleController(self.user_id)
            filters['id__in'] = {line[0] for line in art_contr
                    .read(**art_filters).with_entities(Article.cluster_id)}

    @staticmethod
    def _get_selected(fields, art_f_alias, art_c_alias, filter_on_category):
        """Return selected fields, adapting to either postgres or sqlite"""
        selected_fields = list(fields.values())
        if SQLITE_ENGINE:  # pragma: no cover
            selected_fields.append(func.group_concat(
                    art_f_alias.feed_id).label('feeds_id'))
            if filter_on_category:
                selected_fields.append(func.group_concat(
                        art_c_alias.category_id).label('categories_id'))
        else:
            selected_fields.append(func.array_agg(art_f_alias.feed_id,
                    type_=ARRAY(Integer)).label('feeds_id'))
            if filter_on_category:
                selected_fields.append(func.array_agg(
                        art_c_alias.category_id,
                        type_=ARRAY(Integer)).label('categories_id'))
        return selected_fields

    def _join_on_exist(self, query, alias, attr, value, filters):
        val_col = getattr(alias, attr)
        exist_query = exists(select([val_col])
                .where(and_(alias.cluster_id == Cluster.id,
                            alias.user_id == self.user_id, val_col == value))
                .correlate(Cluster).limit(1))
        return query.join(alias, and_(alias.user_id == self.user_id,
                                      alias.cluster_id == Cluster.id,
                                      *filters))\
                    .filter(exist_query)

    @staticmethod
    def _iter_on_query(query, filter_on_category):
        """For a given query will iter on it, transforming raw rows to proper
        dictionnaries and handling the agreggation around feeds_id and
        categories_id.
        """
        for clu in query:
            row = {}
            for key in JR_FIELDS:
                row[key] = getattr(clu, key)
            if SQLITE_ENGINE:  # pragma: no cover
                row['feeds_id'] = [int(fid) for fid in clu.feeds_id.split(',')]
                if filter_on_category and clu.categories_id:
                    row['categories_id'] = [int(cid)
                            for cid in clu.categories_id.split(',')]
                elif filter_on_category:
                    row['categories_id'] = [0]
            else:
                row['feeds_id'] = clu.feeds_id
                if filter_on_category:
                    row['categories_id'] = [i or 0 for i in clu.categories_id]
            yield row

    def _light_no_filter_query(self, processed_filters):
        """If there's no filter to shorten the query (eg we're just selecting
        all feed with no category) we make a request more adapted to the task.
        """
        sub_query = session.query(*JR_SQLA_FIELDS)\
                           .filter(*processed_filters)\
                           .order_by(Cluster.main_date.desc())\
                           .limit(JR_LENGTH).cte('clu')

        if SQLITE_ENGINE:  # pragma: no cover
            aggreg = func.group_concat(Article.feed_id).label('feeds_id')
        else:
            aggreg = func.array_agg(Article.feed_id).label('feeds_id')
        query = session.query(sub_query, aggreg)\
                .join(Article, Article.cluster_id == sub_query.c.id)
        if self.user_id:
            query = query.filter(Article.user_id == self.user_id)
        yield from self._iter_on_query(query.group_by(*sub_query.c)
                .order_by(sub_query.c.main_date.desc()), False)

    def join_read(self, feed_id=None, **filters):
        filter_on_cat = 'category_id' in filters
        cat_id = filters.pop('category_id', None)
        if self.user_id:
            filters['user_id'] = self.user_id

        self._preprocess_per_article_filters(filters)
        if 'id__in' in filters and not filters['id__in']:
            # filtering by article but did not found anything
            return

        processed_filters = self._to_filters(**filters)
        if feed_id is None and not filter_on_cat:
            # no filter with an interesting index to use, using another query
            yield from self._light_no_filter_query(processed_filters)
            return

        art_feed_alias, art_cat_alias = aliased(Article), aliased(Article)
        # DESC of what's going on below :
        # base query with the above fields and the aggregations
        query = session.query(*self._get_selected(JR_FIELDS,
                art_feed_alias, art_cat_alias, filter_on_cat))

        # adding parent filter, but we can't just filter on one id, because
        # we'll miss all the other parent of the cluster
        if feed_id:
            query = self._join_on_exist(query, art_feed_alias,
                                        'feed_id', feed_id, processed_filters)
        else:
            query = query.join(art_feed_alias,
                               and_(art_feed_alias.user_id == self.user_id,
                                    art_feed_alias.cluster_id == Cluster.id,
                                    *processed_filters))
        if filter_on_cat:
            # joining only if filtering on categories to lighten the query
            # as every article doesn't obligatorily have a category > outerjoin
            query = self._join_on_exist(query, art_cat_alias,
                                        'category_id', cat_id,
                                        processed_filters)

        # applying common filter (read / liked)
        # grouping all the fields so that agreg works on distant ids
        yield from self._iter_on_query(
                query.group_by(*JR_SQLA_FIELDS).filter(*processed_filters)
                     .order_by(Cluster.main_date.desc()).limit(JR_LENGTH),
                filter_on_cat)

    def delete(self, obj_id, delete_articles=True):
        self.update({'id': obj_id}, {'main_article_id': None}, commit=False)
        actrl = ArticleController(self.user_id)
        if delete_articles:
            for art in actrl.read(cluster_id=obj_id):
                actrl.delete_only_article(art, commit=False)
        else:
            actrl.update({'cluster_id': obj_id},
                         {'cluster_id': None,
                          'cluster_reason': None,
                          'cluster_score': None,
                          'cluster_tfidf_with': None,
                          'cluster_tfidf_neighbor_size': None})
        return super().delete(obj_id)

    #
    # Real controllers stuff here
    #

    def count_by_feed(self, **filters):
        return self._count_by(Article.feed_id, **filters)

    def count_by_category(self, **filters):
        return self._count_by(Article.category_id, **filters)

    def _count_by(self, group_on, **filters):
        if self.user_id:
            filters['user_id'] = self.user_id
        return dict(session.query(group_on, func.count(Article.cluster_id))
                              .outerjoin(Cluster,
                                         Article.cluster_id == Cluster.id)
                              .filter(*self._to_filters(**filters))
                              .group_by(group_on).all())
