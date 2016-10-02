from datetime import datetime
from sqlalchemy import (Column, ForeignKey, Index,
                        Boolean, String, Integer, DateTime)
from sqlalchemy.orm import relationship
from bootstrap import db
from web.models.article import Article
from web.models.right_mixin import RightMixin
from web.models.relationships import cluster_as_category, cluster_as_feed


class Cluster(db.Model, RightMixin):
    "Represent an article from a feed."
    id = Column(Integer, primary_key=True)
    cluster_type = Column(String)
    read = Column(Boolean, default=False)
    liked = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.utcnow)

    # denorm
    main_date = Column(DateTime, default=datetime.utcnow)
    main_feed_title = Column(String)
    main_title = Column(String)
    main_link = Column(String, default=None)

    # relationship
    main_article_id = Column(Integer, ForeignKey('article.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    feeds = relationship('Feed', back_populates='clusters',
                         secondary=cluster_as_feed,
                         lazy=True)
    categories = relationship('Category', back_populates='clusters',
                              secondary=cluster_as_category,
                              lazy=True)
    articles = relationship('Article', backref='cluster',
                            cascade='all,delete-orphan', order_by=Article.date,
                            foreign_keys=[Article.cluster_id])

    # index
    cluster_liked_user_id_main_date = Index('liked', 'user_id', 'main_date')
    cluster_read_user_id_main_date = Index('read', 'user_id', 'main_date')

    @property
    def categories_id(self):
        return {category.id for category in self.categories}

    @property
    def feeds_id(self):
        return {feed.id for feed in self.feeds}

    @property
    def icons_url(self):
        return {feed.icon_url for feed in self.feeds}

    @property
    def main_article(self):
        return [article for article in self.articles
                if article.id == self.main_article_id][0]

    # api whitelists
    @staticmethod
    def _fields_base_write():
        return {'read', 'liked'}

    @staticmethod
    def _fields_base_read():
        return {'id', 'user_id', 'categories_id', 'feeds_id',
                'main_link', 'main_title', 'main_feed_title', 'main_date',
                'created_date', 'cluster_type', 'icons_url', 'articles'}

    def __repr__(self):
        return "<Cluster(id=%d, title=%r, date=%r)>" \
                % (self.id, self.main_title, self.main_date)
