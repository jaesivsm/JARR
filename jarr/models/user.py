import re
from sqlalchemy import Boolean, Column, Integer, PickleType, String
from sqlalchemy.orm import relationship, validates

from jarr.bootstrap import Base, conf
from jarr.lib.utils import utc_now
from jarr.models.utc_datetime_type import UTCDateTime


class User(Base):  # type: ignore
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    password = Column(String)
    email = Column(String(254))
    date_created = Column(UTCDateTime, default=utc_now)
    last_connection = Column(UTCDateTime, default=utc_now)
    renew_password_token = Column(String, default='')

    timezone = Column(String, default=conf.timezone)

    # clustering control
    cluster_enabled = Column(Boolean, default=True, nullable=False)
    cluster_tfidf_enabled = Column(Boolean, default=True, nullable=False)
    cluster_same_category = Column(Boolean, default=True, nullable=False)
    cluster_same_feed = Column(Boolean, default=True, nullable=False)
    cluster_wake_up = Column(Boolean, default=True, nullable=False)
    cluster_conf = Column(PickleType, default={})

    # user rights
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_api = Column(Boolean, default=False)

    # oauth identites
    google_identity = Column(String)
    twitter_identity = Column(String)
    facebook_identity = Column(String)
    linuxfr_identity = Column(String)

    # relationships
    categories = relationship(
        'Category', back_populates='user', cascade='all, delete-orphan',
        foreign_keys='[Category.user_id]')
    feeds = relationship(
        'Feed', back_populates='user', cascade='all, delete-orphan',
        foreign_keys='[Feed.user_id]')
    articles = relationship(
        'Article', back_populates='user', cascade='all, delete-orphan',
        foreign_keys='[Article.user_id]')
    clusters = relationship(
        'Cluster', back_populates='user', cascade='all, delete-orphan',
        foreign_keys='[Cluster.user_id]')

    @validates('login')
    def string_cleaning(self, key, value):
        return re.sub(r'[^a-zA-Z0-9_\.]', '', value.strip())

    def __repr__(self):
        """Represents a user with its id."""
        return f"<User {self.login}({self.id})>"
