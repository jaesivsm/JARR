import re
from datetime import datetime
from sqlalchemy.orm import validates
from flask.ext.login import UserMixin

from bootstrap import db
from web.models.right_mixin import RightMixin


class User(db.Model, UserMixin, RightMixin):
    """
    Represent a user.
    """
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(), unique=True)
    password = db.Column(db.String())
    email = db.Column(db.String(254))

    # user rights
    is_active = db.Column(db.Boolean(), default=True)
    is_admin = db.Column(db.Boolean(), default=False)
    is_api = db.Column(db.Boolean(), default=False)

    google_identity = db.Column(db.String())
    twitter_identity = db.Column(db.String())
    facebook_identity = db.Column(db.String())

    date_created = db.Column(db.DateTime(), default=datetime.now)
    last_connection = db.Column(db.DateTime(), default=datetime.now)
    feeds = db.relationship('Feed', backref='subscriber', lazy='dynamic',
                            cascade='all,delete-orphan')
    readability_key = db.Column(db.String(), default='')
    renew_password_token = db.Column(db.String(), default='')

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
