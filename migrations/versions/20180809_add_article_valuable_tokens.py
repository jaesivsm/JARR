"""adding valuable tokens to article

Revision ID: 3abdf17387e5
Revises: 9be35ef7b987
Create Date: 2017-05-10 16:13:43.117796

"""

# revision identifiers, used by Alembic.
revision = '3abdf17387e5'
down_revision = '9be35ef7b987'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('article',
            sa.Column('valuable_tokens', sa.PickleType(), nullable=True))


def downgrade():
    with op.batch_alter_table('article') as batch_op:
        batch_op.drop_column('valuable_tokens')
