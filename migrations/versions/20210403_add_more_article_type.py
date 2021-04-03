"""Add more article type

revision id: 511346f4372e
revises: f4543055e780
create date: 2021-04-03 19:57:53.312419

"""

# revision identifiers, used by alembic.
revision = '511346f4372e'
down_revision = 'f4543055e780'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from jarr.lib.enums import ArticleType


def upgrade():
    types = [atype.value for atype in ArticleType]
    new_article_type = postgresql.ENUM(*types, name='articletype2')
    new_article_type.create(op.get_bind())
    op.alter_column('article', 'article_type', new_article_type)


def downgrade():
    types = [atype.value for atype in ArticleType if atype is not atype.audio]
    article_type = postgresql.ENUM(*types, name='articletype')
    op.alter_column('article', 'article_type', article_type)
