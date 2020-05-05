"""adding bool in feed to trigger reddit integration

Revision ID: 9be35ef7b987
Revises: 8744eda9fa05
Create Date: 2017-05-03 00:28:25.199151

"""

# revision identifiers, used by Alembic.
revision = '9be35ef7b987'
down_revision = '8744eda9fa05'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('feed',
            sa.Column('integration_reddit', sa.Boolean(), nullable=True))


def downgrade():
    with op.batch_alter_table('feed') as batch_op:
        batch_op.drop_column('integration_reddit')
