"""adding tag handling capacities

Revision ID: 9462d9753423
Revises: 835c03754c69
Create Date: 2016-10-08 23:07:57.425931

"""

# revision identifiers, used by Alembic.
revision = '9462d9753423'
down_revision = '835c03754c69'
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.create_table('tag',
            sa.Column('text', sa.String(), nullable=False),
            sa.Column('article_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['article_id'], ['article.id'],
                                    ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('text', 'article_id')
    )

def downgrade():
    op.drop_table('tag')
