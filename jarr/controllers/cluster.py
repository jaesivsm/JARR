import logging
from collections import defaultdict
from datetime import timedelta

from sqlalchemy import Integer, and_, func, or_
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import aliased
from sqlalchemy.sql import exists, select

from jarr.bootstrap import session
from jarr.controllers.article import ArticleController, to_vector
from jarr.lib.article_cleaner import fetch_and_parse
from jarr.lib.clustering_af.grouper import get_best_match_and_score
from jarr.lib.content_generator import generate_content
from jarr.lib.enums import ArticleType, ClusterReason, ReadReason
from jarr.lib.filter import process_filters
from jarr.metrics import ARTICLE_CREATION, CLUSTERING, WORKER_BATCH
from jarr.models import Article, Cluster, Feed
from jarr.utils import get_cluster_pref

from .abstract import AbstractController

logger = logging.getLogger(__name__)
# static values for join_read
__returned_keys = ('main_title', 'id', 'liked', 'read', 'main_article_id',
                   'main_feed_title', 'main_date', 'main_link')
JR_FIELDS = {key: getattr(Cluster, key) for key in __returned_keys}
JR_SQLA_FIELDS = [getattr(Cluster, key) for key in __returned_keys]
JR_PAGE_LENGTH = 30
WAKABLE_REASONS = {ReadReason.marked, ReadReason.mass_marked,
                   ReadReason.filtered}


def get_config(obj, attr):
    if obj.__class__.__name__ == "Article":
        return get_config(obj.feed, attr)
    if obj.__class__.__name__ == "Cluster":
        return all(get_config(article, attr) for article in obj.articles)
    val = getattr(obj, attr)
    if val is not None:
        logger.debug("%r.%s is %r", obj, attr, val)
        return val
    if obj.__class__.__name__ == "Feed" and obj.category_id:
        return get_config(obj.category, attr)
    return get_config(obj.user, attr)


def is_same_ok(article, parent):
    return get_config(article.feed, 'cluster_same_%s' % parent)


class ClusterController(AbstractController):
    _db_cls = Cluster

    def _get_query_for_clustering(self, article, filters, filter_tfidf=False):
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

        feed_join = [Feed.id == Article.feed_id,
                     or_(Feed.cluster_enabled.__eq__(True),
                         Feed.cluster_enabled.__eq__(None))]
        if filter_tfidf:
            feed_join.append(or_(Feed.cluster_tfidf_enabled.__eq__(True),
                                 Feed.cluster_tfidf_enabled.__eq__(None)))

        query = ArticleController(self.user_id).read(**filters)\
                .join(Feed, and_(*feed_join))

        # operations involving categories are complicated, handling in software
        for candidate in query:
            if not get_config(candidate, "cluster_enabled"):
                CLUSTERING.labels(filters="allow", config="target-forbid",
                                  result="miss", match="none").inc()
                continue
            if filter_tfidf \
                    and not get_config(candidate, "cluster_tfidf_enabled"):
                CLUSTERING.labels(filters="allow", config="target-forbid",
                                  result="miss", match="tfidf").inc()
                continue
            yield candidate

    def _get_cluster_by_link(self, article):
        for candidate in self._get_query_for_clustering(article,
                {'link_hash': article.link_hash}):
            article.cluster_reason = ClusterReason.link
            CLUSTERING.labels(filters="allow", config="allow",
                              result="match", match="link_hash").inc()
            return candidate.cluster
        for candidate in self._get_query_for_clustering(article,
                {'link': article.link}):
            article.cluster_reason = ClusterReason.link
            CLUSTERING.labels(filters="allow", config="allow",
                              result="match", match="link").inc()
            return candidate.cluster

    def _get_cluster_by_similarity(self, article):
        neighbors = list(self._get_query_for_clustering(article,
                # article is matchable
                {'vector__ne': None}, filter_tfidf=True))

        min_sample_size = get_cluster_pref(article.feed,
                                           'tfidf_min_sample_size')
        if len(neighbors) < min_sample_size:
            logger.info('only %d docs against %d required, no TFIDF for %r',
                        len(neighbors), min_sample_size, article)
            CLUSTERING.labels(filters="allow", config="sample-size-forbid",
                              result="miss", match="tfidf").inc()
            return None

        best_match, score = get_best_match_and_score(article, neighbors)
        if score > get_cluster_pref(article.feed, 'tfidf_min_score'):
            article.cluster_reason = ClusterReason.tf_idf
            article.cluster_score = int(score * 1000)
            article.cluster_tfidf_neighbor_size = len(neighbors)
            article.cluster_tfidf_with = best_match.id
            CLUSTERING.labels(filters="allow", config="allow",
                              result="match", match="tfidf").inc()
            return best_match.cluster
        CLUSTERING.labels(filters="allow", config="score-forbid",
                          result="miss", match="tfidf").inc()

    def _create_from_article(self, article,
                             cluster_read=None, cluster_liked=False,
                             parsing_result=None):
        cluster = Cluster(user_id=article.user_id)
        article.cluster_reason = ClusterReason.original
        return self.enrich_cluster(cluster, article,
                                   cluster_read, cluster_liked,
                                   force_article_as_main=True,
                                   parsing_result=parsing_result)

    @staticmethod
    def enrich_cluster(cluster, article,
                       cluster_read=None, cluster_liked=False,
                       force_article_as_main=False, parsing_result=None):
        parsing_result = parsing_result or {}
        article.cluster = cluster
        # handling read status
        if cluster.read is None:  # no read status, new cluster
            cluster.read = bool(cluster_read)
        elif cluster_read is not None:  # filters indicate a read status
            cluster.read = cluster.read and cluster_read
            cluster.read_reason = ReadReason.filtered
            logger.debug('marking as read because of filter %r', cluster)
        elif (cluster.read  # waking up a cluster
              and cluster.read_reason in WAKABLE_REASONS
              and get_config(article, 'cluster_wake_up')
              and get_config(cluster, 'cluster_wake_up')):
            cluster.read = False
            logger.debug('waking up %r', cluster)
        # once one article is liked the cluster is liked
        cluster.liked = cluster.liked or cluster_liked
        if force_article_as_main or cluster.main_date > article.date:
            cluster.main_title = parsing_result.get('title', article.title)
            cluster.main_date = article.date
            cluster.main_link = article.link
            cluster.main_feed_title = article.feed.title
            cluster.main_article_id = article.id
        if not cluster.content:
            success, content = generate_content(article, parsing_result)
            if success:
                cluster.content = content
        session.add(cluster)
        session.add(article)
        session.commit()
        ARTICLE_CREATION.labels(read_reason=cluster.read_reason,
                                read='read' if cluster.read else 'unread',
                                cluster=article.cluster_reason.value).inc()
        return cluster

    def clusterize(self, article, filter_result=None):
        """Will add given article to a fitting cluster or create a cluster
        fitting that article."""
        filter_result = filter_result or {}
        allow_clustering = filter_result.get('clustering', True)
        filter_read = filter_result.get('read')
        filter_liked = filter_result.get('liked')
        logger.info('%r - processed filter: %r', article, filter_result)
        cluster_config = get_config(article.feed, 'cluster_enabled')

        # fetching article so that vector comparison is made on full content
        parsing_result = None
        if article.feed.truncated_content:
            parsing_result = fetch_and_parse(article.link)
            if parsing_result.get('parsed_content'):
                article.vector = to_vector(
                        article.title, article.tags, article.content,
                        parsing_result)

        # clustering
        if allow_clustering and cluster_config:
            cluster = self._get_cluster_by_link(article)
            tfidf_config = get_config(article.feed, 'cluster_tfidf_enabled') \
                    and article.article_type not in {ArticleType.image,
                                                     ArticleType.video,
                                                     ArticleType.embedded}
            if not cluster and tfidf_config:
                cluster = self._get_cluster_by_similarity(article)
            elif not cluster and not tfidf_config:
                CLUSTERING.labels(filters="allow", config="forbid",
                                  result="miss", match="tfidf").inc()
                logger.debug("%r - no clustering because tfidf disabled",
                             article)
            if cluster:
                return self.enrich_cluster(cluster, article,
                                           filter_read, filter_liked,
                                           parsing_result=parsing_result)
        else:
            logger.debug("%r - no clustering because filters: %r, config: %r",
                         article, not allow_clustering, not cluster_config)
            CLUSTERING.labels(
                    filters="allow" if allow_clustering else "forbid",
                    config="allow" if cluster_config else "forbid",
                    result="miss", match="none").inc()
        return self._create_from_article(article, filter_read, filter_liked,
                                         parsing_result)

    def clusterize_pending_articles(self):
        results = []
        actrl = ArticleController(self.user_id)
        articles = list(actrl.read(cluster_id=None))
        logger.info('User(%s) got %d articles to clusterize',
                    self.user_id, len(articles))
        WORKER_BATCH.labels(worker_type='clusterizer').observe(len(articles))
        for article in actrl.read(cluster_id=None):
            filter_result = process_filters(article.feed.filters,
                                            {'tags': article.tags,
                                             'title': article.title,
                                             'link': article.link})
            result = self.clusterize(article, filter_result).id
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
    def _iter_on_query(query):
        """For a given query will iter on it, transforming raw rows to proper
        dictionnaries and handling the agreggation around feeds_id and
        categories_id.
        """

        def _ensure_zero_list(clu, key):
            return [i or 0 for i in getattr(clu, key, [])] or [0]

        for clu in query:
            row = {}
            for key in JR_FIELDS:
                row[key] = getattr(clu, key)
            row['feeds_id'] = clu.feeds_id
            row['categories_id'] = _ensure_zero_list(clu, 'categories_id')
            yield row

    def _light_no_filter_query(self, processed_filters,
                               limit=JR_PAGE_LENGTH):
        """If there's no filter to shorten the query (eg we're just selecting
        all feed with no category) we make a request more adapted to the task.
        """
        sub_query = session.query(*JR_SQLA_FIELDS)\
                           .filter(*processed_filters)\
                           .order_by(Cluster.main_date.desc())\
                           .cte('clu')

        aggreg_feed = func.array_agg(Article.feed_id).label('feeds_id')
        aggreg_cat = func.array_agg(Article.category_id).label('categories_id')
        query = (session.query(sub_query, aggreg_feed, aggreg_cat)
                .join(Article, Article.cluster_id == sub_query.c.id)
                .filter(Article.user_id == self.user_id))
        yield from self._iter_on_query(query.group_by(*sub_query.c)
                .order_by(sub_query.c.main_date.desc()).limit(limit))

    def join_read(self, feed_id=None, limit=JR_PAGE_LENGTH, **filters):
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
            yield from self._light_no_filter_query(processed_filters,
                                                   JR_PAGE_LENGTH)
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
                     .order_by(Cluster.main_date.desc())
                     .limit(limit))

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

    def get_unreads(self):
        counters = defaultdict(int)
        for cid, fid, unread in session.query(Article.category_id,
                                              Article.feed_id,
                                              func.count(Cluster.id))\
                .join(Article, and_(Article.cluster_id == Cluster.id,
                                    Article.user_id == self.user_id))\
                .filter(and_(Cluster.user_id == self.user_id,
                             Cluster.read.__eq__(False)))\
                .group_by(Article.category_id, Article.feed_id):
            if cid:
                counters["categ-%d" % cid] += unread
            counters["feed-%d" % fid] = unread
        return counters
