import re
from datetime import datetime
from sqlalchemy.orm import validates
from flask.ext.login import UserMixin

from bootstrap import db


class User(db.Model, UserMixin):
    """
    Represent a user.
    """
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(), unique=True)
    password = db.Column(db.String())
    email = db.Column(db.String(254))

    is_admin = db.Column(db.Boolean(), default=False)
    is_api = db.Column(db.Boolean(), default=False)

    oauth_twitter = db.Column(db.String())
    oauth_facebook = db.Column(db.String())
    oauth_google = db.Column(db.String())

    date_created = db.Column(db.DateTime(), default=datetime.now)
    last_seen = db.Column(db.DateTime(), default=datetime.now)
    feeds = db.relationship('Feed', backref='subscriber', lazy='dynamic',
                            cascade='all,delete-orphan')
    refresh_rate = db.Column(db.Integer, default=60)  # in minutes
    readability_key = db.Column(db.String(), default='')

    @validates('login')
    def validates_login(self, key, value):
        return re.sub('[^a-zA-Z0-9_\.]', '', value)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return '<User %r>' % (self.login)

    def dump(self):
        return {'id': self.id}
