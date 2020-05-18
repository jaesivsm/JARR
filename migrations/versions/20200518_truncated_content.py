"""Adding control column for feed to fetch

Revision ID: 5f7bef70b57a
Revises: 4405e868ef61
Create Date: 2020-05-18 12:27:23.277010

"""
import logging
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '5f7bef70b57a'
down_revision = '4405e868ef61'
branch_labels = None
depends_on = None
logger = logging.getLogger('alembic.' + revision)


def upgrade():
    logger.info('dropping readability_parsed column from articles')
    op.drop_column('article', 'readability_parsed')
    logger.info("adding config on feed with 'truncated_content' column")
    op.add_column('feed',
                  sa.Column('truncated_content', sa.Boolean(),
                            nullable=True))
    op.execute("UPDATE feed SET truncated_content=false;")
    op.alter_column("feed", "truncated_content", nullable=False)

    logger.info("removing the feed_type 'fetch'")
    op.execute("UPDATE feed SET feed_type='classic' WHERE feed_type='fetch';")

    newfeedtype = postgresql.ENUM('classic', 'json', 'tumblr', 'instagram',
                                  'soundcloud', 'reddit', 'koreus', 'twitter',
                                  name='newfeedtype')
    newfeedtype.create(op.get_bind())
    op.execute("""ALTER TABLE feed
                  ALTER COLUMN feed_type SET DATA TYPE newfeedtype
                  USING feed_type::text::newfeedtype;""")
    op.execute("DROP TYPE feedtype;")
    op.execute("ALTER TYPE newfeedtype RENAME TO feedtype;")


def downgrade():
    op.drop_column('feed', 'truncated_content')
    op.add_column('article',
                  sa.Column('readability_parsed', sa.BOOLEAN(),
                            autoincrement=False, nullable=True))

    newfeedtype = postgresql.ENUM('classic', 'json', 'tumblr', 'instagram',
                                  'soundcloud', 'reddit', 'koreus', 'twitter',
                                  'fetch', name='newfeedtype')
    newfeedtype.create(op.get_bind())
    op.execute("""ALTER TABLE feed
                  ALTER COLUMN feed_type SET DATA TYPE newfeedtype
                  USING feed_type::text::newfeedtype;""")
    op.execute("DROP TYPE feedtype;")
    op.execute("ALTER TYPE newfeedtype RENAME TO feedtype;")
