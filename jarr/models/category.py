from jarr.bootstrap import Base
from sqlalchemy import (Boolean, Column, ForeignKeyConstraint, Index, Integer,
                        PickleType, String)
from sqlalchemy.orm import RelationshipProperty, relationship


class Category(Base):  # type: ignore
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
    user: RelationshipProperty = relationship(
        'User', back_populates='categories', uselist=False)
    feeds: RelationshipProperty = relationship(
        'Feed', back_populates='category',
        cascade='all,delete-orphan', uselist=False)
    articles: RelationshipProperty = relationship(
        'Article', back_populates='category', cascade='all,delete-orphan')
    clusters: RelationshipProperty = relationship(
        'Cluster', back_populates='categories',
        foreign_keys='[Article.category_id, Article.cluster_id]',
        secondary='article', overlaps="articles,category,cluster,clusters")

    __table_args__ = (
            ForeignKeyConstraint([user_id], ['user.id'],
                                 ondelete='CASCADE'),
            Index('ix_category_uid', user_id),
    )

    def __repr__(self):
        return f"<Category({self.id})>"
