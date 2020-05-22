from sqlalchemy import (Binary, Column, Enum, ForeignKeyConstraint,
                        Index, Integer, PickleType, String)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship

from jarr.bootstrap import Base
from jarr.lib.enums import ArticleType, ClusterReason
from jarr.lib.utils import utc_now
from jarr.models.utc_datetime_type import UTCDateTime
from jarr.lib.clustering_af.vector import TFIDFVector


class Article(Base):
    "Represent an article from a feed."
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True)
    entry_id = Column(String)
    link = Column(String)
    link_hash = Column(Binary)
    title = Column(String)
    content = Column(String)
    comments = Column(String)
    lang = Column(String)
    date = Column(UTCDateTime, default=utc_now)
    retrieved_date = Column(UTCDateTime, default=utc_now)

    # integration control
    article_type = Column(Enum(ArticleType),
                          default=None, nullable=True)

    # parsing
    tags = Column(PickleType, default=[])
    vector = Column(TSVECTOR)

    _simple_vector = None
    _simple_vector_magnitude = 0

    @property
    def simple_vector(self):
        if self._simple_vector:
            return self._simple_vector
        if self._simple_vector is None:
            self._simple_vector = {}
        if self.vector is not None:
            for word_n_count in self.vector.split():
                word_n_count = word_n_count.split(':', 1)
                word = word_n_count[0]
                count = word_n_count[1] if len(word_n_count) > 1 else ''
                word = word[1:-1]
                self._simple_vector[word] = count.count(',') + 1
                self._simple_vector_magnitude += self._simple_vector[word]
        return self._simple_vector

    @property
    def simple_vector_magnitude(self):
        if not self._simple_vector_magnitude:
            self._simple_vector_magnitude = sum(self.simple_vector.values())
        return self._simple_vector_magnitude

    def get_tfidf_vector(self, frequencies, corpus_size,
                         will_be_left_member=False):
        return TFIDFVector(self.simple_vector,
                           self.simple_vector_magnitude,
                           frequencies, corpus_size,
                           will_be_left_member=will_be_left_member)

    def reset_simple_vector(self):
        self._simple_vector = None
        self._simple_vector_magnitude = 0

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
            Index('ix_article_eid_cid_uid', user_id, category_id, entry_id),
            Index('ix_article_uid_cid_linkh', user_id, category_id, link_hash),
            Index('ix_article_retrdate', retrieved_date),
    )

    def __repr__(self):
        """Represents and article."""
        return "<Article(feed_id=%s, id=%s)>" % (self.feed_id, self.id)
