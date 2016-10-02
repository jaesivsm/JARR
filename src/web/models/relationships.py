from bootstrap import db
from sqlalchemy import Table, Column, Integer, ForeignKey, String


cluster_as_category = Table('cluster_as_category', db.metadata,
        Column('cluster_id', Integer, ForeignKey('cluster.id')),
        Column('category_id', Integer, ForeignKey('category.id')),
)

cluster_as_feed = Table('cluster_as_feed', db.metadata,
        Column('cluster_id', Integer, ForeignKey('cluster.id')),
        Column('feed_id', Integer, ForeignKey('feed.id')),
)
