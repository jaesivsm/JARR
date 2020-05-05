"""readability integration

Revision ID: 493abdb2b73
Revises: 3f83bfe93fc
Create Date: 2016-02-04 23:19:23.086189

"""
import sqlalchemy as sa
from alembic import op

revision = '493abdb2b73'
down_revision = '3f83bfe93fc'


def upgrade():
    op.add_column('article', sa.Column('readability_parsed',
                                       sa.Boolean(), nullable=True))
    op.add_column('feed', sa.Column('readability_auto_parse',
                                    sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('readability_key',
                                    sa.String(), nullable=True))


def downgrade():
    op.drop_column('user', 'readability_key')
    op.drop_column('feed', 'readability_auto_parse')
    op.drop_column('article', 'readability_parsed')
