"""all article will now compare on entry_id, either they have one or not

Revision ID: 835c03754c69
Revises: a7f62d50d366
Create Date: 2016-10-05 10:09:59.178235

"""

# revision identifiers, used by Alembic.
revision = '835c03754c69'
down_revision = 'a7f62d50d366'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from web.models.article import Article


def upgrade():
    op.execute(sa.update(Article).where(Article.entry_id == None)
                                 .values(entry_id=Article.link))


def downgrade():
    pass
