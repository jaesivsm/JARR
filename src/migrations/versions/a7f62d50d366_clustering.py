"""adding tables to support clustering

Revision ID: a7f62d50d366
Revises: 9e3fecc9d031
Create Date: 2016-07-31 19:45:19.889247

"""

# revision identifiers, used by Alembic.
revision = 'a7f62d50d366'
down_revision = '9e3fecc9d031'
branch_labels = None
depends_on = None

from datetime import datetime
from bootstrap import conf
from alembic import op
import sqlalchemy as sa


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
    if 'sqlite' not in conf.SQLALCHEMY_DATABASE_URI:
        op.create_foreign_key(None, 'article', 'cluster',
                            ['cluster_id'], ['id'])
        op.create_foreign_key(None, 'cluster', 'article',
                            ['main_article_id'], ['id'])

        op.execute('CREATE INDEX cluster_uid_date ON cluster '
                   '(user_id, main_date DESC NULLS LAST);')
        op.execute('CREATE INDEX cluster_liked_uid_date ON cluster '
                   '(liked, user_id, main_date DESC NULLS LAST);')
        op.execute('CREATE INDEX cluster_read_uid_date ON cluster '
                   '(read, user_id, main_date DESC NULLS LAST);')

        print('%s - Creating clusters' % datetime.now().isoformat())
        op.execute("""
    INSERT INTO cluster (main_link, user_id, main_date, read, liked)
        SELECT link, user_id, MIN(date), BOOL_AND(readed), BOOL_OR("like")
            FROM article GROUP BY link, user_id;""")

        print('%s - Updating clusters with main article infos'
                % datetime.now().isoformat())
        op.execute(sa.update(Cluster)
                .where(sa.and_(Cluster.main_link == Article.link,
                               Cluster.user_id == Article.user_id,
                               Article.feed_id == Feed.id,
                               Cluster.main_date == Article.date))
                .values(main_title=Article.title,
                        main_feed_title=Feed.title,
                        main_article_id=Article.id))
        op.execute("""UPDATE article SET cluster_id = cluster.id
                      FROM cluster WHERE cluster.main_link = article.link
                                     AND article.user_id = cluster.user_id;""")

    else:
        print('%s - Creating clusters' % datetime.now().isoformat())
        op.execute("""
    INSERT INTO cluster (main_link, user_id, main_date, read, liked)
        SELECT link, user_id, MIN(date), SUM(readed) = COUNT(id),
               SUM("like") > COUNT(id)
            FROM article GROUP BY link, user_id;""")

        WHERE = """WHERE cluster.main_link = article.link
                 AND cluster.user_id = article.user_id
                 AND cluster.main_date = article.date"""

        print('%s - Updating clusters with main article infos'
                % datetime.now().isoformat())
        op.execute("UPDATE cluster SET "
    "main_title = (SELECT article.title FROM article %(WHERE)s), "
    "main_article_id = (SELECT article.id FROM article %(WHERE)s), "
    "main_feed_title = (SELECT feed.title FROM article, feed %(WHERE)s "
                       "AND article.feed_id = feed.id);" % {'WHERE': WHERE})

        print('%s - Updating articles' % datetime.now().isoformat())
        op.execute("""UPDATE article
                      SET cluster_id = (SELECT cluster.id FROM cluster
                                        WHERE cluster.main_link = article.link
                                        AND article.user_id = cluster.user_id);
    """)

    with op.batch_alter_table('article') as batch_op:
        batch_op.drop_column('readed')
        batch_op.drop_column('like')


def downgrade():
    op.add_column('article',
            sa.Column('readed', sa.Boolean(), default=False),
            sa.Column('like', sa.Boolean(), default=False))
    op.drop_constraint(None, 'article', type_='foreignkey')
    with op.batch_alter_table('article') as batch_op:
        batch_op.drop_column('cluster_id')
    op.drop_table('cluster')
