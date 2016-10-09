import logging
import sqlalchemy
from sqlalchemy import func
from collections import Counter
from datetime import datetime, timedelta

from bootstrap import db
from .abstract import AbstractController
from web.controllers import CategoryController, FeedController
from web.models import User, Article
from lib.article_utils import process_filters

logger = logging.getLogger(__name__)


class ArticleController(AbstractController):
    _db_cls = Article

    def challenge(self, ids):
        """Will return each id that wasn't found in the database."""
        for id_ in ids:
            if self.read(**id_).first():
                continue
            yield id_

    def count_by_feed(self, **filters):
        if self.user_id:
            filters['user_id'] = self.user_id
        return dict(db.session.query(Article.feed_id, func.count('id'))
                              .filter(*self._to_filters(**filters))
                              .group_by(Article.feed_id).all())

    def count_by_user_id(self, **filters):
        last_conn_max = datetime.utcnow() - timedelta(days=30)
        return dict(db.session.query(Article.user_id, func.count(Article.id))
                              .filter(*self._to_filters(**filters))
                              .join(User).filter(User.is_active.__eq__(True),
                                        User.last_connection >= last_conn_max)
                              .group_by(Article.user_id).all())

    def create(self, **attrs):
        from web.controllers.cluster import ClusterController
        cluster_contr = ClusterController(self.user_id)
        # handling special denorm for article rights
        assert 'feed_id' in attrs, "must provide feed_id when creating article"
        feed = FeedController(
                attrs.get('user_id', self.user_id)).get(id=attrs['feed_id'])
        if 'user_id' in attrs:
            assert feed.user_id == attrs['user_id'] or self.user_id is None, \
                    "no right on feed %r" % feed.id
        attrs['user_id'], attrs['category_id'] = feed.user_id, feed.category_id

        skipped, read, liked = process_filters(feed.filters, attrs)
        if skipped:
            return None
        article = super().create(**attrs)
        cluster_contr.clusterize(article, read, liked)
        return article

    def update(self, filters, attrs, *args, **kwargs):
        user_id = attrs.get('user_id', self.user_id)
        if 'feed_id' in attrs:
            feed = FeedController().get(id=attrs['feed_id'])
            assert self.user_id is None or feed.user_id == user_id, \
                    "no right on feed %r" % feed.id
            attrs['category_id'] = feed.category_id
        if attrs.get('category_id'):
            cat = CategoryController().get(id=attrs['category_id'])
            assert self.user_id is None or cat.user_id == user_id, \
                    "no right on cat %r" % cat.id
        return super().update(filters, attrs, *args, **kwargs)

    def get_history(self, year=None, month=None):
        "Sort articles by year and month."
        articles_counter = Counter()
        articles = self.read()
        if year is not None:
            articles = articles.filter(
                    sqlalchemy.extract('year', Article.date) == year)
            if month is not None:
                articles = articles.filter(
                        sqlalchemy.extract('month', Article.date) == month)
        articles = articles.order_by('date')
        for article in articles.all():
            if year is not None:
                articles_counter[article.date.month] += 1
            else:
                articles_counter[article.date.year] += 1
        return articles_counter, articles

    def remove_from_all_clusters(self, article_id):
        """Removes article with id == article_id from the cluster it belongs to
        If it's the only article of the cluster will delete the cluster
        Return True if the article is deleted at the end or not
        """
        from web.controllers import ClusterController
        clu_ctrl = ClusterController(self.user_id)
        cluster = self.get(id=article_id).cluster
        if len(cluster.articles) == 1:
            clu_ctrl.delete(cluster.id)
            return False
        clu_ctrl._enrich_cluster(cluster, cluster.articles[1])
        return True

    def delete(self, obj_id, commit=True):
        still_delete_article = self.remove_from_all_clusters(obj_id)
        if still_delete_article:
            obj = self.get(id=obj_id)
            for tag in obj.tag_objs:
                db.session.delete(tag)
            db.session.delete(obj)
            if commit:
                db.session.flush()
                db.session.commit()
            return obj
