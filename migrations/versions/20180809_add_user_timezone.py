"""adding per user timezone

Revision ID: c0cbb689b3c5
Revises: 7c9f11d94eb7
Create Date: 2017-03-13 23:26:54.141776

"""

# revision identifiers, used by Alembic.
revision = 'c0cbb689b3c5'
down_revision = '7c9f11d94eb7'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('user', sa.Column('timezone', sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('timezone')
