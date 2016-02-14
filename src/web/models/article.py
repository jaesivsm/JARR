from bootstrap import db
from datetime import datetime
from sqlalchemy import asc, desc, Index


class Article(db.Model):
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

    def dump(self):
        return {"id": self.id,
                "user_id": self.user_id,
                "entry_id": self.entry_id,
                "title": self.title,
                "link": self.link,
                "content": self.content,
                "readed": self.readed,
                "like": self.like,
                "date": self.date,
                "readability_parsed": self.readability_parsed,
                "retrieved_date": self.retrieved_date,
                "feed_id": self.feed_id,
                "category_id": self.category_id}
