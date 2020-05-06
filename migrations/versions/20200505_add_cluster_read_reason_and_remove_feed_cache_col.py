"""adding read_reason and dropping old column for logging cache reason on feed

Revision ID: 4405e868ef61
Revises: cad754e6b832
Create Date: 2020-05-05 16:28:36.208126

"""
import logging
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '4405e868ef61'
down_revision = 'cad754e6b832'
branch_labels = None
depends_on = None
logger = logging.getLogger('alembic.' + revision)
REASONS = ['read', 'consulted', 'marked', 'mass_marked', 'filtered', 'wake_up']

def upgrade():
    logger.info('adding possible values to read reasons')
    new_read_reason = postgresql.ENUM(*REASONS, name='readreason2')
    new_read_reason.create(op.get_bind())
    op.alter_column('cluster', 'read_reason', new_read_reason)
    logger.info('dropping old column for caching type')
    op.drop_column('feed', 'cache_support_a_im')
    op.drop_column('feed', 'cache_type')
    # old_read_reason = postgresql.ENUM(*REASONS[:-2], name='readreason')
    cache_reason = postgresql.ENUM('status_code_304', 'etag',
                                   'etag_calculated', 'instance_manipulation',
                                   name='cachereason')
    cache_reason.drop(op.get_bind())
    # old_read_reason.drop(op.get_bind())

def downgrade():
    cache_reason = postgresql.ENUM('status_code_304', 'etag',
                                   'etag_calculated', 'instance_manipulation',
                                   name='cachereason')
    cache_reason.create(op.get_bind())
    op.add_column('feed', sa.Column('cache_type', cache_reason,
                                    autoincrement=False, nullable=True))
    op.add_column('feed', sa.Column('cache_support_a_im', sa.BOOLEAN(),
                                    server_default=sa.text('false'),
                                    autoincrement=False, nullable=True))
