"""storing article language

Revision ID: 7d652d333758
Revises: 3abdf17387e5
Create Date: 2017-05-11 16:31:10.726877

"""

# revision identifiers, used by Alembic.
revision = '7d652d333758'
down_revision = '3abdf17387e5'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('article', sa.Column('lang', sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table('article') as batch_op:
        batch_op.drop_column('lang')
