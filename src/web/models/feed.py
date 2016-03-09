from bootstrap import db
from datetime import datetime
from sqlalchemy import desc, Index
from sqlalchemy.orm import validates
from web.models.right_mixin import RightMixin


class Feed(db.Model, RightMixin):
    """
    Represent a feed.
    """
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(), default="")
    description = db.Column(db.String(), default="FR")
    link = db.Column(db.String())
    site_link = db.Column(db.String(), default="")
    enabled = db.Column(db.Boolean(), default=True)
    created_date = db.Column(db.DateTime(), default=datetime.utcnow)
    filters = db.Column(db.PickleType, default=[])
    readability_auto_parse = db.Column(db.Boolean(), default=False)

    # cache handling
    etag = db.Column(db.String(), default="")
    last_modified = db.Column(db.String(), default="")
    last_retrieved = db.Column(db.DateTime(), default=datetime(1970, 1, 1))

    # error logging
    last_error = db.Column(db.String(), default="")
    error_count = db.Column(db.Integer(), default=0)

    # relationship
    icon_url = db.Column(db.String(), db.ForeignKey('icon.url'), default=None)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer(), db.ForeignKey('category.id'))
    articles = db.relationship('Article', backref='source', lazy='dynamic',
                               cascade='all,delete-orphan',
                               order_by=desc("date"))

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
