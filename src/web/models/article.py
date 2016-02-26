from bootstrap import db
from datetime import datetime
from sqlalchemy import asc, desc, Index
from web.models.right_mixin import RightMixin


class Article(db.Model, RightMixin):
    "Represent an article from a feed."
    id = db.Column(db.Integer(), primary_key=True)
    entry_id = db.Column(db.String())
    link = db.Column(db.String())
    title = db.Column(db.String())
    content = db.Column(db.String())
    readed = db.Column(db.Boolean(), default=False)
    like = db.Column(db.Boolean(), default=False)
    date = db.Column(db.DateTime(), default=datetime.utcnow)
    retrieved_date = db.Column(db.DateTime(), default=datetime.utcnow)
    readability_parsed = db.Column(db.Boolean(), default=False)

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    feed_id = db.Column(db.Integer(), db.ForeignKey('feed.id'))
    category_id = db.Column(db.Integer(), db.ForeignKey('category.id'))

    idx_article_uid = Index('user_id')
    idx_article_uid_cid = Index('user_id', 'category_id')
    idx_article_uid_fid = Index('user_id', 'feed_id')

    # api whitelists
    @staticmethod
    def _fields_base_write():
        return {'readed', 'like', 'readability_parsed',
                'feed_id', 'category_id'}

    @staticmethod
    def _fields_base_read():
        return {'id', 'entry_id', 'link', 'title', 'content', 'date',
                'retrieved_date', 'user_id'}

    def previous_article(self):
        """
        Returns the previous article (older).
        """
        return Article.query.filter(Article.date < self.date,
                                    Article.feed_id == self.feed_id)\
                            .order_by(desc("date")).first()

    def next_article(self):
        """
        Returns the next article (newer).
        """
        return Article.query.filter(Article.date > self.date,
                                    Article.feed_id == self.feed_id)\
                            .order_by(asc("date")).first()

    def __repr__(self):
        return "<Article(id=%d, entry_id=%s, title=%r, " \
               "date=%r, retrieved_date=%r)>" % (self.id, self.entry_id,
                       self.title, self.date, self.retrieved_date)
