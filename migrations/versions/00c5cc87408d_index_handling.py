"""better model description and index handling

Revision ID: 00c5cc87408d
Revises: 256acb048a32
Create Date: 2018-02-23 15:21:26.384595
"""
import logging
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '00c5cc87408d'
down_revision = '256acb048a32'
branch_labels = None
depends_on = None

logger = logging.getLogger('alembic.' + revision)


def upgrade():
    logger.info('better model description, adjustements to models')
    op.alter_column('article', 'feed_id',
                    existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('article', 'user_id',
                    existing_type=sa.INTEGER(), nullable=False)
    logger.info('adding link_hash column')
    op.add_column('article', sa.Column('link_hash',
                                       sa.Binary(), nullable=True))
    logger.info('updating link_hash values')
    op.get_bind().execute("""UPDATE article
                             SET link_hash = digest(link, 'SHA1');""")
    logger.info('creating article indexes')
    op.create_index('ix_article_eid_cid_uid', 'article',
                    ['user_id', 'category_id', 'entry_id'], unique=False)
    op.create_index('ix_article_uid_cid_linkh', 'article',
                    ['user_id', 'category_id', 'link_hash'], unique=False)
    op.drop_index('article_uid_fid', table_name='article')
    op.create_index('ix_article_retrdate', 'article',
                    ['retrieved_date'], unique=False)
    op.create_index('ix_article_uid_cid_cluid', 'article',
                    ['user_id', 'category_id', 'cluster_id'], unique=False)
    op.create_index('ix_article_uid_cluid', 'article',
                    ['user_id', 'cluster_id'], unique=False)
    op.create_index('ix_article_uid_fid_cluid', 'article',
                    ['user_id', 'feed_id', 'cluster_id'], unique=False)
    op.drop_constraint('article_user_id_fkey', 'article', type_='foreignkey')
    op.drop_constraint('article_feed_id_fkey', 'article', type_='foreignkey')
    op.drop_constraint('article_category_id_fkey', 'article',
                       type_='foreignkey')
    logger.info('creating article FK')
    op.create_foreign_key(None, 'article', 'user',
                          ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'article', 'category',
                          ['category_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'article', 'feed',
                          ['feed_id'], ['id'], ondelete='CASCADE')
    logger.info('updating category table')
    op.alter_column('category', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_index('ix_category_uid', 'category', ['user_id'], unique=False)
    op.drop_constraint('category_user_id_fkey', 'category', type_='foreignkey')
    op.create_foreign_key(None, 'category', 'user',
                          ['user_id'], ['id'], ondelete='CASCADE')
    logger.info('updating cluster table')
    op.alter_column('cluster', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    logger.info('creating cluster index')
    op.create_index('ix_cluster_liked_uid_date', 'cluster',
                    ['liked', 'user_id', sa.text('main_date DESC NULLS LAST')],
                    unique=False)
    op.create_index('ix_cluster_read_uid_date', 'cluster',
                    ['read', 'user_id', sa.text('main_date DESC NULLS LAST')],
                    unique=False)
    op.create_index('ix_cluster_uid_date', 'cluster',
                    ['user_id', sa.text('main_date DESC NULLS LAST')],
                    unique=False)
    op.create_index('ix_cluster_martid', 'cluster',
                    ['user_id', sa.text('main_article_id DESC NULLS FIRST')],
                    unique=False)
    op.drop_constraint('cluster_user_id_fkey', 'cluster', type_='foreignkey')
    op.create_foreign_key(None, 'cluster', 'user',
                          ['user_id'], ['id'], ondelete='CASCADE')
    logger.info('updating feed table')
    op.alter_column('feed', 'cache_support_a_im',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('false'))
    op.alter_column('feed', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_index('ix_feed_uid', 'feed', ['user_id'], unique=False)
    op.create_index('ix_feed_uid_cid', 'feed',
                    ['user_id', 'category_id'], unique=False)
    op.drop_constraint('feed_category_id_fkey', 'feed', type_='foreignkey')
    op.drop_constraint('feed_user_id_fkey', 'feed', type_='foreignkey')
    op.create_foreign_key(None, 'feed', 'category',
                          ['category_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'feed', 'user',
                          ['user_id'], ['id'], ondelete='CASCADE')


def downgrade():
    op.drop_constraint(None, 'feed', type_='foreignkey')
    op.drop_constraint(None, 'feed', type_='foreignkey')
    op.create_foreign_key('feed_user_id_fkey', 'feed', 'user',
                          ['user_id'], ['id'])
    op.create_foreign_key('feed_category_id_fkey', 'feed', 'category',
                          ['category_id'], ['id'])
    op.alter_column('feed', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('feed', 'cache_support_a_im',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('false'))
    op.drop_constraint(None, 'cluster', type_='foreignkey')
    op.create_foreign_key('cluster_user_id_fkey', 'cluster', 'user',
                          ['user_id'], ['id'])
    op.alter_column('cluster', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_constraint(None, 'category', type_='foreignkey')
    op.create_foreign_key('category_user_id_fkey', 'category', 'user',
                          ['user_id'], ['id'])
    op.alter_column('category', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_constraint(None, 'article', type_='foreignkey')
    op.drop_constraint(None, 'article', type_='foreignkey')
    op.drop_constraint(None, 'article', type_='foreignkey')
    op.create_foreign_key('article_category_id_fkey', 'article', 'category',
                          ['category_id'], ['id'])
    op.create_foreign_key('article_feed_id_fkey', 'article', 'feed',
                          ['feed_id'], ['id'])
    op.create_foreign_key('article_user_id_fkey', 'article', 'user',
                          ['user_id'], ['id'])
    op.alter_column('article', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('article', 'feed_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_index('ix_article_uid_cid_linkh', table_name='article')
