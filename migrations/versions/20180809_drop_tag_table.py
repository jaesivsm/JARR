"""drop tag table

Revision ID: 8079a1cb5874
Revises: 00c5cc87408d
Create Date: 2018-02-23 15:59:24.702040
"""
import logging
from alembic import op
import sqlalchemy as sa

revision = '8079a1cb5874'
down_revision = '00c5cc87408d'
branch_labels = None
depends_on = None
logger = logging.getLogger('alembic.' + revision)


def upgrade():
    logger.info('droping tag table')
    op.drop_table('tag')
    logger.info('using pickled data to store tag on articles')
    op.add_column('article', sa.Column('tags', sa.PickleType(), nullable=True))


def downgrade():
    op.drop_column('article', 'tags')
    op.create_table('tag',
    sa.Column('text', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('article_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['article.id'], name='tag_article_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('text', 'article_id', name='tag_pkey')
    )
