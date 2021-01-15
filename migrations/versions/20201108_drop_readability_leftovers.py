"""Dropping old integration with readability left overs

Revision ID: f4543055e780
Revises: f5978c8a8740
Create Date: 2020-11-08 20:28:31.145702

"""
import logging

import sqlalchemy as sa
from alembic import op

logger = logging.getLogger(__name__)
revision = 'f4543055e780'
down_revision = 'f5978c8a8740'
branch_labels = None
depends_on = None


def upgrade():
    logger.info('dropping readability_key column from user')
    op.drop_column('user', 'readability_key')


def downgrade():
    op.add_column('user', sa.Column('readability_key',
                                    sa.String(), nullable=True))
