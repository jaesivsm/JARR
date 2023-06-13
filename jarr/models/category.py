from jarr.bootstrap import Base
from sqlalchemy import (Boolean, Column, ForeignKeyConstraint, Index, Integer,
                        PickleType, String)
from sqlalchemy.orm import relationship, validates


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
    user = relationship(
        'User', back_populates='categories', uselist=False)
    feeds = relationship(
        'Feed', back_populates='category',
        cascade='all,delete-orphan', uselist=False)
    articles = relationship(
        'Article', back_populates='category', cascade='all,delete-orphan')
    clusters = relationship(
        'Cluster', back_populates='categories',
        foreign_keys='[Article.category_id, Article.cluster_id]',
        secondary='article', overlaps="articles,category,cluster,clusters")

    __table_args__ = (
            ForeignKeyConstraint([user_id], ['user.id'],
                                 ondelete='CASCADE'),
            Index('ix_category_uid', user_id),
    )

    @validates("name")
    def string_cleaning(self, key, value):
        return str(value if value is not None else '').strip()

    def __repr__(self):
        return f"<Category({self.id})>"
