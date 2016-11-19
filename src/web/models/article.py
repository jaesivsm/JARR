from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from bootstrap import db
from lib.utils import utc_now
from web.models.utc_datetime_type import UTCDateTime
from web.models.right_mixin import RightMixin


class Article(db.Model, RightMixin):
    "Represent an article from a feed."
    id = Column(Integer, primary_key=True)
    entry_id = Column(String)
    link = Column(String)
    title = Column(String)
    content = Column(String)
    date = Column(UTCDateTime, default=utc_now)
    retrieved_date = Column(UTCDateTime, default=utc_now)
    readability_parsed = Column(Boolean, default=False)

    # foreign keys
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    feed_id = Column(Integer, ForeignKey('feed.id', ondelete='CASCADE'))
    category_id = Column(Integer,
                         ForeignKey('category.id', ondelete='CASCADE'))
    cluster_id = Column(Integer, ForeignKey('cluster.id'))

    # relationships
    user = relationship('User', back_populates='articles')
    cluster = relationship('Cluster', back_populates='articles',
                           foreign_keys=[cluster_id])
    category = relationship('Category', back_populates='articles',
                            foreign_keys=[category_id])
    feed = relationship('Feed', back_populates='articles',
                        foreign_keys=[feed_id])
    tag_objs = relationship('Tag', back_populates='article',
                            cascade='all,delete-orphan',
                            lazy=False,
                            foreign_keys='[Tag.article_id]')
    tags = association_proxy('tag_objs', 'text')

    # index
    article_uid_cluid = Index('user_id', 'cluster_id')
    article_uid_fid_cluid = Index('user_id', 'feed_id', 'cluster_id')
    article_uid_cid_cluid = Index('user_id', 'category_id', 'cluster_id')
    article_eid_cid_uid = Index('entry_id', 'category_id', 'user_id')
    article_link_cid_uid = Index('link', 'category_id', 'user_id')
    article_retrdate = Index('retrieved_date')

    # api whitelists
    @staticmethod
    def _fields_base_write():
        return {'readability_parsed', 'feed_id', 'category_id'}

    @staticmethod
    def _fields_base_read():
        return {'id', 'entry_id', 'link', 'title', 'content', 'date',
                'retrieved_date', 'user_id', 'tags'}

    @staticmethod
    def _fields_api_write():
        return {'tags'}

    def __repr__(self):
        return "<Article(id=%d, entry_id=%s, title=%r, " \
               "date=%r, retrieved_date=%r)>" % (self.id, self.entry_id,
                       self.title, self.date, self.retrieved_date)
