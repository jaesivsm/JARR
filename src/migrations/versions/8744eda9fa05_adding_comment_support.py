"""adding comment support

Revision ID: 8744eda9fa05
Revises: c0cbb689b3c5
Create Date: 2017-05-01 10:18:16.528311

"""

# revision identifiers, used by Alembic.
revision = '8744eda9fa05'
down_revision = 'c0cbb689b3c5'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('article', sa.Column('comments', sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table('article') as batch_op:
        batch_op.drop_column('comments')
