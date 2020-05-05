"""adding more reasons for clustering

Revision ID: 256acb048a32
Revises: e2d7db861709
Create Date: 2017-07-31 11:49:16.345244

"""
from alembic import op
import sqlalchemy as sa

revision = '256acb048a32'
down_revision = 'e2d7db861709'
branch_labels = None
depends_on = None
enum_fields = ['status_code_304', 'etag', 'etag_calculated']


def upgrade():
    from sqlalchemy.dialects import postgresql
    postgresql.ENUM(*enum_fields, name='cachereason')\
                    .create(op.get_bind())
    op.add_column('feed', sa.Column('cache_support_a_im', sa.Boolean,
                                    nullable=False, server_default='FALSE'))
    op.add_column('feed', sa.Column('cache_type',
                                    sa.Enum(*enum_fields, name='cachereason'),
                                    nullable=True))
    op.add_column('article',sa.Column('cluster_tfidf_neighbor_size',
                                      sa.Integer(), nullable=True))
    op.add_column('article', sa.Column('cluster_tfidf_with',
                                       sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table('feed') as batch_op:
        batch_op.drop_column('cache_type')
        batch_op.drop_column('cache_support_a_im')

    with op.batch_alter_table('article') as batch_op:
        batch_op.drop_column('cluster_tfidf_with')
        batch_op.drop_column('cluster_tfidf_neighbor_size')
