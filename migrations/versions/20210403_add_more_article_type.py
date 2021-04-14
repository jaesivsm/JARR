"""Add more article type

revision id: 511346f4372e
revises: f4543055e780
create date: 2021-04-03 19:57:53.312419

"""
import logging

import sqlalchemy as sa
from alembic import op

revision = '511346f4372e'
down_revision = 'f4543055e780'
branch_labels = None
depends_on = None

logger = logging.getLogger('alembic.' + revision)


def upgrade():
    logger.info('adding audio as a possible article type')
    op.execute("ALTER TYPE articletype ADD VALUE IF NOT EXISTS 'audio';")
    op.add_column('article',
                  sa.Column('order_in_cluster', sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table('article') as batch_op:
        batch_op.drop_column('order_in_cluster')
