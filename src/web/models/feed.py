from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Index, Integer,
                        PickleType, String)
from sqlalchemy.orm import relationship, validates

from bootstrap import db
from web.models.right_mixin import RightMixin


class Feed(db.Model, RightMixin):
    """
    Represent a feed.
    """
    id = Column(Integer, primary_key=True)
    title = Column(String, default="")
    description = Column(String, default="")
    link = Column(String)
    site_link = Column(String, default="")
    enabled = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    filters = Column(PickleType, default=[])
    readability_auto_parse = Column(Boolean, default=False)

    # cache handling
    etag = Column(String, default="")
    last_modified = Column(String, default="")
    last_retrieved = Column(DateTime, default=datetime(1970, 1, 1))

    # error logging
    last_error = Column(String, default="")
    error_count = Column(Integer, default=0)

    # foreign keys
    icon_url = Column(String, ForeignKey('icon.url'), default=None)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    category_id = Column(Integer,
                         ForeignKey('category.id', ondelete='CASCADE'))

    # relationships
    user = relationship('User', back_populates='feeds')
    category = relationship('Category', back_populates='feeds')
    articles = relationship('Article', back_populates='feed',
                            cascade='all,delete-orphan')
    clusters = relationship('Cluster', back_populates='feeds',
            foreign_keys='[Article.feed_id, Article.cluster_id]',
            secondary='article')

    # index
    idx_feed_uid_cid = Index('user_id', 'category_id')
    idx_feed_uid = Index('user_id')

    # api whitelists
    @staticmethod
    def _fields_base_write():
        return {'title', 'description', 'link', 'site_link', 'enabled',
                'filters', 'readability_auto_parse', 'last_error',
                'error_count', 'category_id'}

    @staticmethod
    def _fields_base_read():
        return {'id', 'user_id', 'icon_url', 'last_retrieved'}

    @staticmethod
    def _fields_api_write():
        return {'etag', 'last_modified'}

    def __repr__(self):
        return '<Feed %r>' % (self.title)

    @validates('title')
    def validates_title(self, key, value):
        return str(value).strip()

    @validates('description')
    def validates_description(self, key, value):
        return str(value).strip()
