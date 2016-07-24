"""readability integration

Revision ID: 493abdb2b73
Revises: 3f83bfe93fc
Create Date: 2016-02-04 23:19:23.086189

"""

# revision identifiers, used by Alembic.
revision = '493abdb2b73'
down_revision = '3f83bfe93fc'
from bootstrap import conf
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('article', sa.Column('readability_parsed',
                                       sa.Boolean(), nullable=True))
    op.add_column('feed', sa.Column('readability_auto_parse',
                                    sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('readability_key',
                                    sa.String(), nullable=True))


def downgrade():
    if 'sqlite' not in conf.SQLALCHEMY_DATABASE_URI:
        op.drop_column('user', 'readability_key')
        op.drop_column('feed', 'readability_auto_parse')
        op.drop_column('article', 'readability_parsed')
