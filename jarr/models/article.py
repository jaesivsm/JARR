from sqlalchemy import (Boolean, Column, Integer, PickleType,
                        String, Enum, Index, ForeignKeyConstraint)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR

from jarr.lib.utils import utc_now
from jarr.lib.reasons import ClusterReason
from jarr.bootstrap import Base
from jarr.models.utc_datetime_type import UTCDateTime


class Article(Base):
    "Represent an article from a feed."
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True)
    entry_id = Column(String)
    link = Column(String)
    title = Column(String)
    content = Column(String)
    comments = Column(String)
    lang = Column(String)
    date = Column(UTCDateTime, default=utc_now)
    retrieved_date = Column(UTCDateTime, default=utc_now)
    readability_parsed = Column(Boolean, default=False)
    tags = Column(PickleType, default=[])
    vector = Column(TSVECTOR)

    @property
    def simple_vector(self):
        if getattr(self, '_simple_vector', None) is not None:
            return self._simple_vector
        self._simple_vector = {}
        for word_n_count in self.vector.split():
            try:
                word, count = word_n_count.split(':')
            except Exception:  # no :count if there's only one
                self._simple_vector[word_n_count[1:-1]] = 1
            else:
                self._simple_vector[word[1:-1]] = count.count(',')
        return self._simple_vector

    # reasons
    cluster_reason = Column(Enum(ClusterReason), default=None)
    cluster_score = Column(Integer, default=None)
    cluster_tfidf_neighbor_size = Column(Integer, default=None)
    cluster_tfidf_with = Column(Integer, default=None)

    # foreign keys
    user_id = Column(Integer, nullable=False)
    feed_id = Column(Integer, nullable=False)
    category_id = Column(Integer)
    cluster_id = Column(Integer)

    # relationships
    user = relationship('User', back_populates='articles')
    cluster = relationship('Cluster', back_populates='articles',
                           foreign_keys=[cluster_id])
    category = relationship('Category', back_populates='articles',
                            foreign_keys=[category_id])
    feed = relationship('Feed', back_populates='articles',
                        foreign_keys=[feed_id])

    __table_args__ = (
            ForeignKeyConstraint([user_id], ['user.id'], ondelete='CASCADE'),
            ForeignKeyConstraint([feed_id], ['feed.id'], ondelete='CASCADE'),
            ForeignKeyConstraint([category_id], ['category.id'],
                                 ondelete='CASCADE'),
            ForeignKeyConstraint([cluster_id], ['cluster.id']),
            Index('ix_article_uid_cluid', user_id, cluster_id),
            Index('ix_article_uid_fid_cluid', user_id, feed_id, cluster_id),
            Index('ix_article_uid_cid_cluid',
                  user_id, category_id, cluster_id),
            Index('ix_article_eid_cid_uid', entry_id, category_id, user_id),
            Index('ix_article_link_cid_uid', link, category_id, user_id),
            Index('ix_article_retrdate', retrieved_date),
    )

    def __repr__(self):
        return "<Article(id=%d, entry_id=%r, title=%r, " \
               "date=%s, retrieved_date=%s)>" % (self.id, self.entry_id,
                       self.title, self.date.isoformat(),
                       self.retrieved_date.isoformat())
