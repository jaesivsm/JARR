from datetime import datetime
from sqlalchemy import (Column, Index, ForeignKey,
                        Integer, String, Boolean, DateTime)
from bootstrap import db
from web.models.right_mixin import RightMixin


class Article(db.Model, RightMixin):
    "Represent an article from a feed."
    id = Column(Integer, primary_key=True)
    entry_id = Column(String)
    link = Column(String)
    title = Column(String)
    content = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    retrieved_date = Column(DateTime, default=datetime.utcnow)
    readability_parsed = Column(Boolean, default=False)

    # relationships
    user_id = Column(Integer, ForeignKey('user.id'))
    feed_id = Column(Integer, ForeignKey('feed.id'))
    category_id = Column(Integer, ForeignKey('category.id'))
    cluster_id = Column(Integer, ForeignKey('cluster.id'))

    # index
    idx_article_eid_cid_uid = Index('entry_id', 'category_id', 'user_id')
    idx_article_link_cid_uid = Index('link', 'category_id', 'user_id')
    idx_article_retrdate = Index('retrieved_date')

    # api whitelists
    @staticmethod
    def _fields_base_write():
        return {'readability_parsed', 'feed_id', 'category_id'}

    @staticmethod
    def _fields_base_read():
        return {'id', 'entry_id', 'link', 'title', 'content', 'date',
                'retrieved_date', 'user_id'}

    def __repr__(self):
        return "<Article(id=%d, entry_id=%s, title=%r, " \
               "date=%r, retrieved_date=%r)>" % (self.id, self.entry_id,
                       self.title, self.date, self.retrieved_date)
