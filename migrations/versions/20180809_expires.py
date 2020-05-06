"""adding expires field

Revision ID: 7c9f11d94eb7
Revises: 9462d9753423
Create Date: 2016-11-13 17:01:25.606470

"""

# revision identifiers, used by Alembic.
revision = '7c9f11d94eb7'
down_revision = '9462d9753423'
branch_labels = None
depends_on = None
from datetime import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    unix_start = datetime(1970, 1, 1)
    op.add_column('feed', sa.Column('expires', sa.DateTime(),
            nullable=True, default=unix_start, server_default=str(unix_start)))


def downgrade():
    with op.batch_alter_table('feed') as batch_op:
        batch_op.drop_column('expires')
