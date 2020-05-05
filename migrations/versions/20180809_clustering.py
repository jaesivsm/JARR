"""adding tables to support clustering

Revision ID: a7f62d50d366
Revises: 9e3fecc9d031
Create Date: 2016-07-31 19:45:19.889247

"""
import logging
import sqlalchemy as sa
from alembic import op

revision = 'a7f62d50d366'
down_revision = '9e3fecc9d031'
branch_labels = None
depends_on = None

logger = logging.getLogger('alembic.' + revision)


def upgrade():
    op.create_table('cluster',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('cluster_type', sa.String(), nullable=True),
            sa.Column('main_link', sa.String(), nullable=True),
            sa.Column('read', sa.Boolean(), nullable=True),
            sa.Column('liked', sa.Boolean(), nullable=True),
            sa.Column('created_date', sa.DateTime(), nullable=True),
            sa.Column('main_date', sa.DateTime(), nullable=True),
            sa.Column('main_feed_title', sa.String(), nullable=True),
            sa.Column('main_title', sa.String(), nullable=True),
            sa.Column('main_article_id', sa.Integer(), nullable=True),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['user.id']),
            sa.PrimaryKeyConstraint('id'))
    op.add_column('category',
            sa.Column('cluster_on_title', sa.Boolean(), default=False))
    op.add_column('article',
            sa.Column('cluster_id', sa.Integer(), nullable=True))

    from web.models import Cluster, Feed, Article
    op.create_foreign_key(None, 'article', 'cluster',
                            ['cluster_id'], ['id'])
    op.create_foreign_key(None, 'cluster', 'article',
                            ['main_article_id'], ['id'])

    logger.info('Creating clusters')
    op.execute("""
INSERT INTO cluster (main_link, user_id, main_date, read, liked)
    SELECT link, user_id, MIN(date), BOOL_AND(readed), BOOL_OR("like")
        FROM article GROUP BY link, user_id;""")

    logger.info('Updating clusters with main article infos')
    op.execute(sa.update(Cluster)
            .where(sa.and_(Cluster.main_link == Article.link,
                            Cluster.user_id == Article.user_id,
                            Article.feed_id == Feed.id,
                            Cluster.main_date == Article.date))
            .values(main_title=Article.title,
                    main_feed_title=Feed.title,
                    main_article_id=Article.id))

    logger.info('setting article to clusters')
    op.execute("""UPDATE article SET cluster_id = cluster.id
                    FROM cluster WHERE cluster.main_link = article.link
                                    AND article.user_id = cluster.user_id;""")

    with op.batch_alter_table('article') as batch_op:
        batch_op.drop_column('readed')
        batch_op.drop_column('like')

    logger.info('creating index 0/6')
    op.execute('CREATE INDEX article_cluid ON article (cluster_id);')
    logger.info('creating index 1/6')
    op.execute('CREATE INDEX article_uid_cid_cluid ON article'
                '(user_id, category_id, cluster_id);')
    logger.info('creating index 2/6')
    op.execute('CREATE INDEX article_uid_fid_cluid ON article'
                '(user_id, feed_id, cluster_id);')
    logger.info('creating index 3/6')
    op.execute('CREATE INDEX cluster_uid_date ON cluster '
                '(user_id, main_date DESC NULLS LAST);')
    logger.info('creating index 4/6')
    op.execute('CREATE INDEX cluster_liked_uid_date ON cluster '
                '(liked, user_id, main_date DESC NULLS LAST);')
    logger.info('creating index 5/6')
    op.execute('CREATE INDEX cluster_read_uid_date ON cluster '
                '(read, user_id, main_date DESC NULLS LAST);')
    logger.info('creating index 6/6')
    op.execute('CREATE INDEX cluster_uid_mlink ON cluster '
                '(user_id, main_link);')

def downgrade():
    op.add_column('article',
            sa.Column('readed', sa.Boolean(), default=False),
            sa.Column('like', sa.Boolean(), default=False))
    op.drop_constraint(None, 'article', type_='foreignkey')
    with op.batch_alter_table('article') as batch_op:
        batch_op.drop_column('cluster_id')
    op.drop_table('cluster')
