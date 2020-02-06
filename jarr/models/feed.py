from sqlalchemy import (Boolean, Column, Integer, PickleType, String, Enum,
                        Index, ForeignKeyConstraint)
from sqlalchemy.orm import relationship, validates

from jarr.lib.utils import utc_now
from jarr.lib.const import UNIX_START
from jarr.lib.reasons import CacheReason
from jarr.bootstrap import Base
from jarr.models.utc_datetime_type import UTCDateTime


class Feed(Base):
    __tablename__ = 'feed'

    id = Column(Integer, primary_key=True)
    title = Column(String, default="")
    description = Column(String, default="")
    link = Column(String)
    site_link = Column(String, default="")
    enabled = Column(Boolean, default=True)
    created_date = Column(UTCDateTime, default=utc_now)
    filters = Column(PickleType, default=[])
    readability_auto_parse = Column(Boolean, default=False)
    integration_reddit = Column(Boolean, default=False)

    # clustering control
    cluster_enabled = Column(Boolean, default=True)
    cluster_tfidf_enabled = Column(Boolean, default=True)
    cluster_same_category = Column(Boolean, default=True)
    cluster_same_feed = Column(Boolean, default=True)
    cluster_wake_up = Column(Boolean, default=True)
    cluster_conf = Column(PickleType, default={})

    # cache reasons
    cache_type = Column(Enum(CacheReason), default=None)
    cache_support_a_im = Column(Boolean, default=False)

    # cache handling
    etag = Column(String, default="")
    last_modified = Column(String, default="")
    last_retrieved = Column(UTCDateTime, default=UNIX_START)
    expires = Column(UTCDateTime, default=UNIX_START)

    # error logging
    last_error = Column(String, default="")
    error_count = Column(Integer, default=0)

    # foreign keys
    icon_url = Column(String, default=None)
    user_id = Column(Integer, nullable=False)
    category_id = Column(Integer)

    # relationships
    user = relationship('User', back_populates='feeds')
    category = relationship('Category', back_populates='feeds')
    articles = relationship('Article', back_populates='feed',
                            cascade='all,delete-orphan')
    clusters = relationship('Cluster', back_populates='feeds',
            foreign_keys='[Article.feed_id, Article.cluster_id]',
            secondary='article')

    __table_args__ = (
            ForeignKeyConstraint([user_id], ['user.id'], ondelete='CASCADE'),
            ForeignKeyConstraint([category_id], ['category.id'],
                                 ondelete='CASCADE'),
            ForeignKeyConstraint([icon_url], ['icon.url']),
            Index('ix_feed_uid', user_id),
            Index('ix_feed_uid_cid', user_id, category_id),
    )

    def __repr__(self):
        return '<Feed %r>' % (self.title)

    @property
    def abs_icon_url(self):
        from flask import url_for
        return url_for('feed_icon', url=self.icon_url, _external=True)

    @validates('title')
    @staticmethod
    def validates_title(key, value):
        return str(value).strip()

    @validates('description')
    @staticmethod
    def validates_description(key, value):
        return str(value).strip()
