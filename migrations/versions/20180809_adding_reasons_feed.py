"""adding reasons field

Revision ID: e2d7db861709
Revises: 7d652d333758
Create Date: 2017-07-25 12:05:47.958845

"""
from alembic import op
import sqlalchemy as sa
from jarr.lib.enums import ClusterReason, ReadReason

revision = 'e2d7db861709'
down_revision = '7d652d333758'
branch_labels = None
depends_on = None


def upgrade():
    from sqlalchemy.dialects import postgresql
    postgresql.ENUM(*[rr.value for rr in ReadReason], name='readreason')\
                    .create(op.get_bind())
    postgresql.ENUM(*[cr.value for cr in ClusterReason],
                    name='clusterreason')\
                    .create(op.get_bind())

    op.add_column('article',
                  sa.Column('cluster_reason',
                            sa.Enum('original', 'link', 'title', 'tf_idf',
                                    name='clusterreason'),
                  nullable=True))
    op.add_column('article',
                  sa.Column('cluster_score', sa.Integer(), nullable=True))
    op.add_column('cluster',
                  sa.Column('read_reason',
                            sa.Enum('read', 'consulted', 'marked',
                                    'mass_marked', 'filtered',
                                    name='readreason'),
                            nullable=True))


def downgrade():
    with op.batch_alter_table('cluster') as batch_op:
        batch_op.drop_column('read_reason')
    with op.batch_alter_table('article') as batch_op:
        batch_op.drop_column('cluster_score')
        batch_op.drop_column('cluster_reason')
