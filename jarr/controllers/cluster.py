import logging
from datetime import timedelta

from sqlalchemy import Integer, and_, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import aliased
from sqlalchemy.sql import exists, select

from jarr.lib.filter import process_filters
from jarr.lib.reasons import ClusterReason, ReadReason
from jarr.lib.clustering_af.grouper import get_best_match_and_score

from jarr.utils import get_cluster_pref
from jarr.bootstrap import session
from jarr.controllers.article import ArticleController
from jarr.models import Article, Cluster, Feed, Category, User

from .abstract import AbstractController

logger = logging.getLogger(__name__)
# static values for join_read
__returned_keys = ('main_title', 'id', 'liked', 'read', 'main_article_id',
                   'main_feed_title', 'main_date', 'main_link')
JR_FIELDS = {key: getattr(Cluster, key) for key in __returned_keys}
JR_SQLA_FIELDS = [getattr(Cluster, key) for key in __returned_keys]
JR_LENGTH = 1000


def _get_parent_attr(obj, attr):
    return (getattr(obj.user, attr) and getattr(obj.category, attr, True)
            and getattr(obj.feed, attr))


def is_same_ok(obj, parent):
    return _get_parent_attr(obj, 'cluster_same_%s' % parent)


class ClusterController(AbstractController):
    _db_cls = Cluster

    def _get_query_for_clustering(self, article, filters, join_filters=None):
        time_delta = timedelta(
                days=get_cluster_pref(article.feed, 'time_delta'))
        date_cond = {'date__lt': article.date + time_delta,
                     'date__gt': article.date - time_delta}
        retr_cond = {'retrieved_date__lt': article.retrieved_date + time_delta,
                     'retrieved_date__gt': article.retrieved_date - time_delta}
        filters.update({'cluster_id__ne': None,
                        'user_id': article.user_id,
                        'id__ne': article.id,
                        '__or__': [date_cond, retr_cond]})
        if article.category_id and not is_same_ok(article, 'category'):
            filters['category_id__ne'] = article.category_id
        if not is_same_ok(article, 'feed'):
            filters['feed_id__ne'] = article.feed_id

        query = ArticleController(self.user_id).read(**filters)\
                .join(Feed, Feed.id == Article.feed_id)\
                .join(User, User.id == Article.user_id)\
                .filter(User.cluster_enabled.__eq__(True),
                        Feed.cluster_enabled.__eq__(True))

        for join_filter in join_filters or []:
            query = query.filter(join_filter)

        # operations involving categories are complicated, handling in software
        for candidate in query:
            if candidate.category_id:
                if not candidate.category.cluster_enabled:
                    continue
            yield candidate

    def _get_cluster_by_link(self, article):
        for candidate in self._get_query_for_clustering(article,
                {'link': article.link}):
            article.cluster_reason = ClusterReason.link
            return candidate.cluster

    def _get_cluster_by_similarity(self, article):
        query = self._get_query_for_clustering(article,
                # article is matchable
                {'vector__ne': None},
                (User.cluster_tfidf_enabled.__eq__(True),
                 Feed.cluster_tfidf_enabled.__eq__(True))
                )

        neighbors = [neighbor for neighbor in query
                     if not neighbor.category_id
                        or neighbor.category.cluster_tfidf_enabled]

        min_sample_size = get_cluster_pref(article.feed,
                'tfidf_min_sample_size')
        if len(neighbors) < min_sample_size:
            logger.info('only %d docs against %d required, no TFIDF for %r',
                        len(neighbors), min_sample_size, article)
            return None

        best_match, score = get_best_match_and_score(article, neighbors)
        if score > get_cluster_pref(article.feed, 'tfidf_min_score'):
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
        if _get_parent_attr(article, 'cluster_enabled'):
            cluster = self._get_cluster_by_link(article)
            if not cluster \
                    and _get_parent_attr(article, 'cluster_tfidf_enabled'):
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
        """Return selected fields"""
        selected_fields = list(fields.values())
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

    def list_feeds_w_unread_count(self):
        fields = Feed.id, Category.id, Feed.title, Category.name
        return session.query(*(fields + (func.count(Cluster.id),)))\
                .outerjoin(Article, and_(Article.feed_id == Feed.id,
                                         Article.user_id == self.user_id))\
                .outerjoin(Cluster, and_(Article.cluster_id == Cluster.id,
                                         Cluster.user_id == self.user_id,
                                         Cluster.read.__eq__(False)))\
                .outerjoin(Category, and_(Feed.category_id == Category.id,
                                          Category.user_id == self.user_id))\
                .filter(Feed.user_id == self.user_id)\
                .group_by(*fields)
