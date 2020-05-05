"""droping old indexes

Revision ID: 33c6542730e6
Revises: a987c6ce888d
Create Date: 2018-08-30 15:09:41.541800

"""
import logging
from alembic import op

revision = '33c6542730e6'
down_revision = 'a987c6ce888d'
branch_labels = None
depends_on = None
logger = logging.getLogger('alembic.' + revision)

def upgrade():
    logger.info('droping old indexes')
    op.drop_index('article_uid', table_name='article')
    op.drop_index('article_uid_cid_cluid', table_name='article')
    op.drop_index('article_uid_cluid', table_name='article')
    op.drop_index('article_uid_fid_cluid', table_name='article')
    op.drop_index('article_uid_fid_eid', table_name='article')
    op.drop_index('cluster_liked_uid_date', table_name='cluster')
    op.drop_index('cluster_read_uid', table_name='cluster')
    op.drop_index('cluster_read_uid_cluid', table_name='cluster')
    op.drop_index('cluster_read_uid_date', table_name='cluster')
    op.drop_index('idx_feed_uid_cid', table_name='feed')


def downgrade():
    op.create_index('idx_feed_uid_cid', 'feed', ['user_id', 'category_id'], unique=False)
    op.create_index('cluster_read_uid_date', 'cluster', ['read', 'user_id', 'main_date'], unique=False)
    op.create_index('cluster_read_uid_cluid', 'cluster', ['read', 'user_id', 'id'], unique=False)
    op.create_index('cluster_read_uid', 'cluster', ['read', 'user_id', 'id'], unique=False)
    op.create_index('cluster_liked_uid_date', 'cluster', ['liked', 'user_id', 'main_date'], unique=False)
    op.create_index('article_uid_fid_eid', 'article', ['user_id', 'feed_id', 'entry_id'], unique=False)
    op.create_index('article_uid_fid_cluid', 'article', ['user_id', 'feed_id', 'cluster_id'], unique=False)
    op.create_index('article_uid_cluid', 'article', ['user_id', 'cluster_id'], unique=False)
    op.create_index('article_uid_cid_cluid', 'article', ['user_id', 'category_id', 'cluster_id'], unique=False)
    op.create_index('article_uid', 'article', ['user_id'], unique=False)
