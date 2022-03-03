from jarr.bootstrap import Base
from jarr.lib.enums import ReadReason
from jarr.lib.utils import utc_now
from jarr.models.article import Article
from jarr.models.utc_datetime_type import UTCDateTime
from sqlalchemy import (Boolean, Column, Enum, ForeignKey,
                        ForeignKeyConstraint, Index, Integer, PickleType,
                        String)
from sqlalchemy.orm import RelationshipProperty, relationship


class Cluster(Base):  # type: ignore
    "Represent a cluster of articles from one or several feeds"
    __tablename__ = 'cluster'

    id = Column(Integer, primary_key=True)
    cluster_type = Column(String)
    read = Column(Boolean, default=False)
    liked = Column(Boolean, default=False)
    created_date = Column(UTCDateTime, default=utc_now)
    content = Column(PickleType, default={})

    # denorm
    main_date = Column(UTCDateTime, default=utc_now)
    main_feed_title = Column(String)
    main_title = Column(String)
    main_link = Column(String, default=None)

    # reasons
    read_reason = Column(Enum(ReadReason), default=None)

    # foreign keys
    user_id = Column(Integer, nullable=False)
    main_article_id = Column(
        Integer,
        ForeignKey('article.id', name='fk_article_id', use_alter=True))

    # relationships
    user: RelationshipProperty = relationship(
        'User', back_populates='clusters')
    main_article: RelationshipProperty = relationship(
        Article, uselist=False, foreign_keys=main_article_id)
    articles: RelationshipProperty = relationship(
        Article, back_populates='cluster', foreign_keys=[Article.cluster_id],
        order_by=Article.date.asc())
    feeds: RelationshipProperty = relationship(
        'Feed', back_populates='clusters', secondary='article',
        foreign_keys=[Article.feed_id, Article.cluster_id],
        overlaps="articles,clusters,cluster,feed")
    categories: RelationshipProperty = relationship(
        'Category', back_populates='clusters', secondary='article',
        foreign_keys=[Article.cluster_id, Article.category_id],
        overlaps="articles,category,cluster,clusters,feeds")

    __table_args__ = (
            ForeignKeyConstraint([user_id], ['user.id'], ondelete='CASCADE'),
            Index('ix_cluster_uid_date',
                  user_id, main_date.desc().nullslast()),
            Index('ix_cluster_liked_uid', liked, user_id),
            Index('ix_cluster_read_uid', read, user_id),
            # used by cluster deletion in FeedController.delete
            Index('ix_cluster_uid_martid',
                  user_id, main_article_id.nullsfirst()),
            # triggered by article.ondelete
            Index('ix_cluster_martid', main_article_id.nullslast()),
    )

    @property
    def categories_id(self):
        return {category.id for category in self.categories}

    @property
    def feeds_id(self):
        return {feed.id for feed in self.feeds}

    @property
    def icons_url(self):
        return {feed.icon_url for feed in self.feeds}

    def __repr__(self):
        return (f"<Cluster(id={self.id}, title={self.main_title!r}, "
                f" date={self.main_date!r})>")
