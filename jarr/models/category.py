from sqlalchemy import (Column, Integer, String, Boolean, PickleType,
                        Index, ForeignKeyConstraint)
from sqlalchemy.orm import relationship

from jarr.bootstrap import Base


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    # clustering control
    cluster_enabled = Column(Boolean, default=None, nullable=True)
    cluster_tfidf_enabled = Column(Boolean, default=None, nullable=True)
    cluster_same_category = Column(Boolean, default=None, nullable=True)
    cluster_same_feed = Column(Boolean, default=None, nullable=True)
    cluster_wake_up = Column(Boolean, default=None, nullable=True)
    cluster_conf = Column(PickleType, default={})

    # foreign keys
    user_id = Column(Integer, nullable=False)

    # relationships
    user = relationship('User', back_populates='categories')
    feeds = relationship('Feed', back_populates='category',
                         cascade='all,delete-orphan')
    articles = relationship('Article', back_populates='category',
                            cascade='all,delete-orphan')
    clusters = relationship('Cluster', back_populates='categories',
            foreign_keys='[Article.category_id, Article.cluster_id]',
            secondary='article')

    __table_args__ = (
            ForeignKeyConstraint([user_id], ['user.id'],
                                 ondelete='CASCADE'),
            Index('ix_category_uid', user_id),
    )

    def __repr__(self):
        return "<Category(%s)>" % self.id
