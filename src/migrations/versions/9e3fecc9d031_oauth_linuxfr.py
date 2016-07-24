"""empty message

Revision ID: 9e3fecc9d031
Revises: 122ac0c356c
Create Date: 2016-04-17 22:36:18.734849

"""

# revision identifiers, used by Alembic.
revision = '9e3fecc9d031'
down_revision = '122ac0c356c'
branch_labels = None
depends_on = None

from bootstrap import conf
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('user',
            sa.Column('linuxfr_identity', sa.String(), nullable=True))


def downgrade():
    if 'sqlite' not in conf.SQLALCHEMY_DATABASE_URI:
        op.drop_column('user', 'linuxfr_identity')
