from bootstrap import db
from datetime import datetime
from sqlalchemy import desc, Index


class Feed(db.Model):
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

    def __repr__(self):
        return '<Feed %r>' % (self.title)

    def dump(self):
        return {"id": self.id,
                "user_id": self.user_id,
                "category_id": self.category_id,
                "title": self.title,
                "description": self.description,
                "link": self.link,
                "site_link": self.site_link,
                "etag": self.etag,
                "enabled": self.enabled,
                "readability_auto_parse": self.readability_auto_parse,
                "filters": self.filters,
                "icon_url": self.icon_url,
                "error_count": self.error_count,
                "last_error": self.last_error,
                "created_date": self.created_date,
                "last_modified": self.last_modified,
                "last_retrieved": self.last_retrieved}
