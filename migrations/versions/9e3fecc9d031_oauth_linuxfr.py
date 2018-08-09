"""adding linuxfr as an oauth provider

Revision ID: 9e3fecc9d031
Revises: 122ac0c356c
Create Date: 2016-04-17 22:36:18.734849

"""
import sqlalchemy as sa
from alembic import op
from jarr.bootstrap import conf


revision = '9e3fecc9d031'
down_revision = '122ac0c356c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user',
            sa.Column('linuxfr_identity', sa.String(), nullable=True))


def downgrade():
    if 'sqlite' not in conf.sqlalchemy.db_uri:
        op.drop_column('user', 'linuxfr_identity')
