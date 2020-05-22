"""new article content management

Revision ID: ce7bfcdd21fc
Revises: 33c6542730e6
Create Date: 2018-08-30 15:22:11.039954

"""
import logging
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from jarr.lib.clustering_af.postgres_casting import LANG_TO_PSQL_MAPPING

revision = 'ce7bfcdd21fc'
down_revision = '33c6542730e6'
branch_labels = None
depends_on = None
logger = logging.getLogger('alembic.' + revision)


def upgrade():
    logger.info('new article content management')
    op.add_column('article',
            sa.Column('vector', postgresql.TSVECTOR(), nullable=True))
    op.drop_column('article', 'valuable_tokens')

    for code, pg_language in LANG_TO_PSQL_MAPPING.items():
        logger.info('vectorizing lang=%s', code)
        op.execute("""UPDATE article SET vector=
        setweight(to_tsvector(%r, coalesce(title, '')), 'A') ||
        setweight(to_tsvector(%r, coalesce(content, '')), 'B')
        WHERE lang ilike '%s%%';""" % (pg_language, pg_language, code))


def downgrade():
    op.add_column('article', sa.Column('valuable_tokens', postgresql.BYTEA(),
                                       autoincrement=False, nullable=True))
    op.drop_column('article', 'vector')
