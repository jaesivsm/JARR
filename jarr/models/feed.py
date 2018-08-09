from sqlalchemy import (Boolean, Column, Integer, PickleType, String, Enum,
                        Index, ForeignKeyConstraint)
from sqlalchemy.orm import relationship, validates

from jarr_common.utils import utc_now
from jarr_common.const import UNIX_START
from jarr_common.reasons import CacheReason
from jarr.bootstrap import Base
from jarr.models.utc_datetime_type import UTCDateTime
from jarr.models.right_mixin import RightMixin


class Feed(Base, RightMixin):
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

    # api whitelists
    @staticmethod
    def _fields_base_write():
        return {'title', 'description', 'link', 'site_link', 'enabled',
                'filters', 'readability_auto_parse', 'last_error',
                'error_count', 'category_id', 'integration_reddit'}

    @staticmethod
    def _fields_base_read():
        return {'id', 'user_id', 'icon_url', 'last_retrieved', 'expires'}

    @staticmethod
    def _fields_api_write():
        return {'etag', 'last_modified', 'expires',
                'cache_support_a_im', 'cache_type'}

    def __repr__(self):
        return '<Feed %r>' % (self.title)

    @validates('title')
    def validates_title(self, key, value):
        return str(value).strip()

    @validates('description')
    def validates_description(self, key, value):
        return str(value).strip()

    custom_api_types = {
            'filters': {'action': 'append', 'type': dict, 'default': []},
    }
