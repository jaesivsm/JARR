from flask import url_for
from sqlalchemy import (Boolean, Column, Enum, ForeignKeyConstraint, Index,
                        Integer, PickleType, String)
from sqlalchemy.orm import relationship, validates

from jarr.bootstrap import Base
from jarr.lib.const import UNIX_START
from jarr.lib.enums import FeedStatus, FeedType
from jarr.lib.utils import utc_now
from jarr.models.utc_datetime_type import UTCDateTime


class Feed(Base):
    __tablename__ = 'feed'

    id = Column(Integer, primary_key=True)
    title = Column(String, default="")
    description = Column(String, default="")
    link = Column(String)
    site_link = Column(String, default="")
    status = Column(Enum(FeedStatus), default=FeedStatus.active,
                    nullable=False)
    created_date = Column(UTCDateTime, default=utc_now)
    filters = Column(PickleType, default=[])

    # integration control
    feed_type = Column(Enum(FeedType),
                       default=FeedType.classic, nullable=False)
    truncated_content = Column(Boolean, default=False, nullable=False)

    # clustering control
    cluster_enabled = Column(Boolean, default=None, nullable=True)
    cluster_tfidf_enabled = Column(Boolean, default=None, nullable=True)
    cluster_same_category = Column(Boolean, default=None, nullable=True)
    cluster_same_feed = Column(Boolean, default=None, nullable=True)
    cluster_wake_up = Column(Boolean, default=None, nullable=True)
    cluster_conf = Column(PickleType, default={})

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
        """Represents a feed with title and id."""
        return '<Feed %r(%r)>' % (self.title, self.id)

    @property
    def abs_icon_url(self):
        return url_for('feed_icon', url=self.icon_url, _external=True)

    @validates('title')
    @staticmethod
    def validates_title(key, value):
        return str(value).strip()

    @validates('description')
    @staticmethod
    def validates_description(key, value):
        return str(value).strip()

    @property
    def crawler(self):
        from jarr.crawler.crawlers import AbstractCrawler
        for crawler_cls in AbstractCrawler.browse_subcls():
            if self.feed_type is crawler_cls.feed_type:
                return crawler_cls(self)
        raise ValueError('No crawler for %r' % self.feed_type)
