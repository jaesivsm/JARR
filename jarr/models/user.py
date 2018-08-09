import re

from flask_login import UserMixin
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship, validates

from jarr_common.utils import utc_now
from jarr.bootstrap import Base, conf
from jarr.models.utc_datetime_type import UTCDateTime
from jarr.models.right_mixin import RightMixin


class User(Base, UserMixin, RightMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    password = Column(String)
    email = Column(String(254))
    date_created = Column(UTCDateTime, default=utc_now)
    last_connection = Column(UTCDateTime, default=utc_now)
    readability_key = Column(String, default='')
    renew_password_token = Column(String, default='')

    timezone = Column(String, default=conf.babel.timezone)
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
    categories = relationship('Category', back_populates='user',
                              cascade='all, delete-orphan',
                              foreign_keys='[Category.user_id]')
    feeds = relationship('Feed', back_populates='user',
                         cascade='all, delete-orphan',
                         foreign_keys='[Feed.user_id]')
    articles = relationship('Article', back_populates='user',
                            cascade='all, delete-orphan',
                            foreign_keys='[Article.user_id]')
    clusters = relationship('Cluster', back_populates='user',
                            cascade='all, delete-orphan',
                            foreign_keys='[Cluster.user_id]')

    # api whitelists
    @staticmethod
    def _fields_base_write():
        return {'login', 'password', 'email', 'readability_key',
                'google_identity', 'twitter_identity', 'facebook_identity'}

    @staticmethod
    def _fields_base_read():
        return {'date_created', 'last_connection'}

    @validates('login')
    def validates_login(self, key, value):
        return re.sub(r'[^a-zA-Z0-9_\.]', '', value.strip())
