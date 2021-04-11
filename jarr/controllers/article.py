import logging
from datetime import timedelta

from sqlalchemy import func
from werkzeug.exceptions import Forbidden, Unauthorized

from jarr.bootstrap import session
from jarr.controllers import CategoryController, FeedController
from jarr.lib.clustering_af.postgres_casting import to_vector
from jarr.lib.utils import digest, utc_now
from jarr.models import Article, User

from .abstract import AbstractController

logger = logging.getLogger(__name__)


class ArticleController(AbstractController):
    _db_cls = Article

    def challenge(self, ids):
        """Will return each id that wasn't found in the database."""
        for id_ in ids:
            if self.read(**id_).with_entities(self._db_cls.id).first():
                continue
            yield id_

    def count_by_feed(self, **filters):
        if self.user_id:
            filters['user_id'] = self.user_id
        return dict(session.query(Article.feed_id, func.count('id'))
                           .filter(*self._to_filters(**filters))
                           .group_by(Article.feed_id).all())

    def count_by_user_id(self, **filters):
        conn_max = utc_now() - timedelta(days=30)
        return dict(session.query(Article.user_id, func.count(Article.id))
                           .filter(*self._to_filters(**filters))
                           .join(User).filter(User.is_active.__eq__(True),
                                              User.last_connection >= conn_max)
                           .group_by(Article.user_id).all())

    @staticmethod
    def get_user_id_with_pending_articles():
        for row in (session.query(Article.user_id)
                           .filter(Article.cluster_id.__eq__(None))
                           .group_by(Article.user_id)):
            yield row[0]

    @staticmethod
    def enhance(article):
        save = False
        if article.feed.truncated_content:
            vector = article.content_generator.get_vector()
            if vector is not None:
                article.vector = vector
                save = True
            for key in 'title', 'lang', 'tags':
                value = article.content_generator.extracted_infos.get(key)
                if value and getattr(article, key) != value:
                    setattr(article, key, value)
                    save = True
        if save:
            session.add(article)
            session.commit()

    def create(self, **attrs):
        # handling special denorm for article rights
        if 'feed_id' not in attrs:
            raise Unauthorized("must provide feed_id when creating article")
        feed = FeedController(
                attrs.get('user_id', self.user_id)).get(id=attrs['feed_id'])
        if 'user_id' in attrs and not (
                feed.user_id == attrs['user_id'] or self.user_id is None):
            raise Forbidden("no right on feed %r" % feed.id)
        attrs['user_id'], attrs['category_id'] = feed.user_id, feed.category_id
        attrs['vector'] = to_vector(attrs)
        if not attrs.get('link_hash') and attrs.get('link'):
            attrs['link_hash'] = digest(attrs['link'], alg='sha1', out='bytes')
        return super().create(**attrs)

    def update(self, filters, attrs, return_objs=False, commit=True):
        user_id = attrs.get('user_id', self.user_id)
        if 'feed_id' in attrs:
            feed = FeedController().get(id=attrs['feed_id'])
            if not (self.user_id is None or feed.user_id == user_id):
                raise Forbidden("no right on feed %r" % feed.id)
            attrs['category_id'] = feed.category_id
        if attrs.get('category_id'):
            cat = CategoryController().get(id=attrs['category_id'])
            if not (self.user_id is None or cat.user_id == user_id):
                raise Forbidden("no right on cat %r" % cat.id)
        return super().update(filters, attrs, return_objs, commit)

    def remove_from_cluster(self, article):
        """Removes article with id == article_id from the cluster it belongs to
        If it's the only article of the cluster will delete the cluster
        Return True if the article is deleted at the end or not
        """
        from jarr.controllers.cluster import ClusterController
        from jarr.controllers.article_clusterizer import Clusterizer
        if not article.cluster_id:
            return
        clu_ctrl = ClusterController(self.user_id)
        cluster = clu_ctrl.read(id=article.cluster_id).first()
        if not cluster:
            return

        try:
            new_art = next(new_art for new_art in cluster.articles
                           if new_art.id != article.id)
        except StopIteration:
            # only on article in cluster, deleting cluster
            clu_ctrl.delete(cluster.id, delete_articles=False)
        else:
            if cluster.main_article_id == article.id:
                cluster.main_article_id = None
                Clusterizer(article.user_id).enrich_cluster(
                        cluster, new_art, cluster.read, cluster.liked,
                        force_article_as_main=True)
        self.update({'id': article.id},
                    {'cluster_id': None,
                     'cluster_reason': None,
                     'cluster_score': None,
                     'cluster_tfidf_with': None,
                     'cluster_tfidf_neighbor_size': None})

    @staticmethod
    def delete_only_article(article, commit):
        session.delete(article)
        if commit:
            session.flush()
            session.commit()
        return article

    def delete(self, obj_id, commit=True):
        article = self.get(id=obj_id)
        self.remove_from_cluster(article)
        session.delete(article)
        return self.delete_only_article(article, commit=commit)
