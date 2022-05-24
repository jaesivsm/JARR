"""Adding `Feed.unread_count` column

Revision ID: f67f8fbefe1c
Revises: 511346f4372e
Create Date: 2022-05-24 15:37:02.985536

"""

# revision identifiers, used by Alembic.
revision = 'f67f8fbefe1c'
down_revision = '511346f4372e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('feed', sa.Column('unread_count', sa.Integer(),
                                    nullable=True, default=0))

def downgrade():
    op.drop_column('feed', 'unread_count')
