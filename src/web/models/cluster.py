from sqlalchemy import Boolean, Column, ForeignKey, Index, \
                       Integer, String, Enum
from sqlalchemy.orm import relationship

from bootstrap import db
from lib.utils import utc_now
from lib.reasons import ReadReason
from web.models.article import Article
from web.models.utc_datetime_type import UTCDateTime
from web.models.right_mixin import RightMixin


class Cluster(db.Model, RightMixin):
    "Represent a cluster of articles from one or several feeds"
    id = Column(Integer, primary_key=True)
    cluster_type = Column(String)
    read = Column(Boolean, default=False)
    liked = Column(Boolean, default=False)
    created_date = Column(UTCDateTime, default=utc_now)

    # denorm
    main_date = Column(UTCDateTime, default=utc_now)
    main_feed_title = Column(String)
    main_title = Column(String)
    main_link = Column(String, default=None)

    # reasons
    read_reason = Column(Enum(ReadReason), default=None)

    # foreign keys
    main_article_id = Column(Integer,
            ForeignKey('article.id', name='fk_article_id', use_alter=True))
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))

    # relationships
    user = relationship('User', back_populates='clusters')
    main_article = relationship('Article', uselist=False,
                                foreign_keys=[main_article_id])
    articles = relationship('Article', back_populates='cluster',
            foreign_keys=[Article.cluster_id],
            order_by=Article.date.asc())
    feeds = relationship('Feed', back_populates='clusters',
            secondary='article',
            foreign_keys=[Article.feed_id, Article.cluster_id])
    categories = relationship('Category', back_populates='clusters',
            secondary='article',
            foreign_keys=[Article.cluster_id, Article.category_id])

    # index
    ix_cluster_uid_date = Index('user_id', 'main_date DESC NULLS LAST')
    ix_cluster_liked_uid_date = Index('liked', 'user_id',
                                      'main_date DESC NULLS LAST')
    ix_cluster_read_uid_date = Index('read', 'user_id',
                                     'main_date DESC NULLS LAST')

    @property
    def categories_id(self):
        return {category.id for category in self.categories}

    @property
    def feeds_id(self):
        return {feed.id for feed in self.feeds}

    @property
    def icons_url(self):
        return {feed.icon_url for feed in self.feeds}

    # api whitelists
    @staticmethod
    def _fields_base_write():
        return {'read', 'liked', 'read_reason'}

    @staticmethod
    def _fields_base_read():
        return {'id', 'user_id', 'categories_id', 'feeds_id',
                'main_link', 'main_title', 'main_feed_title', 'main_date',
                'created_date', 'cluster_type', 'articles', 'main_article_id'}

    def __repr__(self):
        return "<Cluster(id=%d, title=%r, date=%r)>" \
                % (self.id, self.main_title, self.main_date)
