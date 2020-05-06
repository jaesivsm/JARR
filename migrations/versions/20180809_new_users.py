"""moving on to the new version of the user table

Revision ID: 122ac0c356c
Revises: 493abdb2b73
Create Date: 2016-02-14 02:20:24.341526

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table


revision = '122ac0c356c'
down_revision = '493abdb2b73'
branch_labels = None
depends_on = None


def get_tables():
    role = table('role',
                 column('name', sa.String),
                 column('user_id', sa.Integer))
    user = table('user',
            column('id', sa.Integer),
            column('is_active', sa.Boolean),
            column('is_admin', sa.Boolean),
            column('last_connection', sa.DateTime),
            column('last_seen', sa.DateTime),
            column('login', sa.String),
            column('email', sa.String),
            column('password', sa.String),
            column('pwdhash', sa.String))
    return user, role


def upgrade():
    op.add_column('user',
            sa.Column('google_identity', sa.String(), nullable=True))
    op.add_column('user',
            sa.Column('twitter_identity', sa.String(), nullable=True))
    op.add_column('user',
            sa.Column('facebook_identity', sa.String(), nullable=True))
    op.add_column('user', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('is_admin', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('is_api', sa.Boolean(), nullable=True))
    op.add_column('user',
            sa.Column('last_connection', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('login', sa.String(), nullable=True))
    op.add_column('user', sa.Column('password', sa.String(), nullable=True))
    op.add_column('user',
            sa.Column('renew_password_token', sa.String(), nullable=True))

    user, _ = get_tables()
    op.execute(user.update().values(
        {'login': user.c['email'], 'password': user.c['pwdhash'],
         'is_active': op.inline_literal(True),
         'last_connection': user.c['last_seen']}))
    is_admin_val = op.inline_literal('t')
    op.get_bind().execute('UPDATE "user" SET is_admin=%s '
            'WHERE "user".id = (SELECT role.id FROM role '
            'WHERE role.name = %s)' % (is_admin_val,
                                       op.inline_literal('admin')))

    op.create_index('idc_category_uid', 'category', ['user_id'])
    op.create_index('idc_feed_uid', 'feed', ['user_id'])
    op.create_index('idc_feed_uid_cid', 'feed', ['user_id', 'category_id'])
    op.create_index('idc_article_uid', 'article', ['user_id'])
    op.create_index('idc_article_uid_cid', 'article', ['user_id', 'feed_id'])
    op.create_index('idc_article_uid_fid', 'article',
                    ['user_id', 'category_id'])

    op.drop_table('role')
    op.create_unique_constraint(None, 'user', ['login'])
    op.drop_column('user', 'last_seen')
    op.drop_column('user', 'activation_key')
    op.drop_column('user', 'nickname')
    op.drop_column('user', 'pwdhash')


def downgrade():
    op.add_column('user', sa.Column('pwdhash', sa.VARCHAR(), nullable=True))
    op.add_column('user', sa.Column('nickname', sa.VARCHAR(), nullable=True))
    op.add_column('user',
            sa.Column('activation_key', sa.VARCHAR(length=86), nullable=True))
    op.add_column('user', sa.Column('last_seen', sa.DATETIME(), nullable=True))

    op.drop_index('idc_category_uid', 'category')
    op.drop_index('idc_feed_uid', 'feed')
    op.drop_index('idc_feed_uid_cid', 'feed')
    op.drop_index('idc_article_uid', 'article')
    op.drop_index('idc_article_uid_cid', 'article')
    op.drop_index('idc_article_uid_fid', 'article')
    op.drop_column('user', 'password')
    op.drop_column('user', 'login')
    op.drop_column('user', 'last_connection')
    op.drop_column('user', 'is_api')
    op.drop_column('user', 'is_admin')
    op.drop_column('user', 'is_active')
    op.drop_column('user', 'google_identity')
    op.drop_column('user', 'facebook_identity')
    op.drop_column('user', 'twitter_identity')
    op.drop_column('user', 'renew_password_token')
    op.create_table('role',
            sa.Column('id', sa.INTEGER(), nullable=False),
            sa.Column('name', sa.VARCHAR(), nullable=True),
            sa.Column('user_id', sa.INTEGER(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name'))
