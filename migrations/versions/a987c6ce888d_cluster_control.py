"""adding cluster control options on every level

Revision ID: a987c6ce888d
Revises: 00c5cc87408d
Create Date: 2018-08-01 18:34:00.415937

"""
import logging
from alembic import op
import sqlalchemy as sa

revision = 'a987c6ce888d'
down_revision = '8079a1cb5874'
branch_labels = None
depends_on = None
logger = logging.getLogger('alembic.' + revision)
CLUSTER_CONF_OPTIONS = ['cluster_enabled', 'cluster_tfidf_enabled',
                        'cluster_same_category', 'cluster_same_feed',
                        'cluster_wake_up']


def upgrade():
    op.drop_column('category', 'cluster_on_title')
    for table in 'user', 'feed', 'category':
        logger.info('adding cluster control options on %s', table)
        for option in CLUSTER_CONF_OPTIONS:
            op.add_column(table, sa.Column(option, sa.Boolean(),
                                           default=None, nullable=True))
        op.add_column(table, sa.Column('cluster_conf', sa.PickleType(),
                                        default={}, nullable=True))

    logger.info('setting default options to true for users')
    op.execute('UPDATE "user" SET %s;'
               % ', '.join(["%s=true" % opt for opt in CLUSTER_CONF_OPTIONS]))
    for option in CLUSTER_CONF_OPTIONS:
        op.alter_column('user', option, nullable=False)


def downgrade():
    for table in 'user', 'feed', 'category':
        for option in CLUSTER_CONF_OPTIONS:
            op.drop_column(table, option)
    op.add_column('category', sa.Column('cluster_on_title',
        sa.BOOLEAN(), autoincrement=False, nullable=True))
