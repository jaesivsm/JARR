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
from jarr.controllers.article import LANG_TO_PSQL_MAPPING


def upgrade():
    print('%s - new article content management' % datetime.now().isoformat())
    op.add_column('article',
            sa.Column('vector', postgresql.TSVECTOR(), nullable=True))
    op.drop_column('article', 'valuable_tokens')
    op.add_column('cluster', sa.Column('content', sa.String(), nullable=True))

    for code, pg_language in LANG_TO_PSQL_MAPPING.items():
        print('  %s - vectorizing lang=%s'
                % (datetime.now().isoformat(), code))
        op.execute("""UPDATE article SET vector=
        setweight(to_tsvector(%r, coalesce(title, '')), 'A') ||
        setweight(to_tsvector(%r, coalesce(content, '')), 'B')
        WHERE lang ilike '%s%%';""" % (pg_language, pg_language, code))

def downgrade():
    op.drop_column('cluster', 'content')
    op.add_column('article', sa.Column('valuable_tokens', postgresql.BYTEA(),
                                       autoincrement=False, nullable=True))
    op.drop_column('article', 'vector')
