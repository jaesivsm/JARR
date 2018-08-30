"""new article content management

Revision ID: ce7bfcdd21fc
Revises: 33c6542730e6
Create Date: 2018-08-30 15:22:11.039954

"""

# revision identifiers, used by Alembic.
revision = 'ce7bfcdd21fc'
down_revision = '33c6542730e6'
branch_labels = None
depends_on = None
from datetime import datetime
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    print('%s - new article content management' % datetime.now().isoformat())
    op.add_column('article', sa.Column('vector', postgresql.TSVECTOR(), nullable=True))
    op.drop_column('article', 'valuable_tokens')
    op.add_column('cluster', sa.Column('content', sa.String(), nullable=True))


def downgrade():
    op.drop_column('cluster', 'content')
    op.add_column('article', sa.Column('valuable_tokens', postgresql.BYTEA(), autoincrement=False, nullable=True))
    op.drop_column('article', 'vector')
