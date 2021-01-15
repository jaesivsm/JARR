"""improving index and queries for main cluster listing

Revision ID: f5978c8a8740
Revises: 5f7bef70b57a
Create Date: 2020-06-03 12:04:58.696679

"""
import logging
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f5978c8a8740'
down_revision = '5f7bef70b57a'
branch_labels = None
depends_on = None
logger = logging.getLogger('alembic.' + revision)


def upgrade():
    logger.info('creating new indexes sized for main cluster listing')
    op.create_index('ix_article_uid_fid_eid', 'article',
                    ['user_id', 'feed_id', 'entry_id'], unique=False)
    op.create_index('ix_cluster_liked_uid', 'cluster',
                    ['liked', 'user_id'], unique=False)
    op.create_index('ix_cluster_read_uid', 'cluster',
                    ['read', 'user_id'], unique=False)
    logger.info('dropping unused indexes')
    op.drop_index('ix_article_eid_cid_uid', table_name='article')
    op.drop_index('ix_cluster_liked_uid_date', table_name='cluster')
    op.drop_index('ix_cluster_read_uid_date', table_name='cluster')


def downgrade():
    op.create_index('ix_cluster_read_uid_date', 'cluster',
                    ['read', 'user_id', 'main_date'], unique=False)
    op.create_index('ix_cluster_liked_uid_date', 'cluster',
                    ['liked', 'user_id', 'main_date'], unique=False)
    op.create_index('ix_article_eid_cid_uid', 'article',
                    ['user_id', 'category_id', 'entry_id'], unique=False)
    op.drop_index('ix_article_uid_fid_eid', table_name='article')
    op.drop_index('ix_cluster_read_uid', table_name='cluster')
    op.drop_index('ix_cluster_liked_uid', table_name='cluster')
