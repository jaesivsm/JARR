import re
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime
from sqlalchemy.orm import validates, relationship
from flask_login import UserMixin

from bootstrap import db
from web.models.right_mixin import RightMixin
from web.models.category import Category
from web.models.feed import Feed
from web.models.article import Article
from web.models.cluster import Cluster


class User(db.Model, UserMixin, RightMixin):
    """
    Represent a user.
    """
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    password = Column(String)
    email = Column(String(254))
    date_created = Column(DateTime, default=datetime.utcnow)
    last_connection = Column(DateTime, default=datetime.utcnow)
    readability_key = Column(String, default='')
    renew_password_token = Column(String, default='')

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
    categories = relationship('Category', backref='user',
                              cascade='all, delete-orphan',
                            foreign_keys=[Category.user_id])
    feeds = relationship('Feed', backref='user',
                         cascade='all, delete-orphan',
                            foreign_keys=[Feed.user_id])
    articles = relationship('Article', backref='user',
                            cascade='all, delete-orphan',
                            foreign_keys=[Article.user_id])
    clusters = relationship('Cluster', backref='user',
                            cascade='all, delete-orphan',
                            foreign_keys=[Cluster.user_id])

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
        return re.sub('[^a-zA-Z0-9_\.]', '', value.strip())
