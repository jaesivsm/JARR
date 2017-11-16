from datetime import timedelta

from lib.utils import utc_now
from web.controllers import (ArticleController, CategoryController,
                             FeedController, UserController)
from web.models import User, Category, Feed, Cluster, Article, Tag, Icon


def populate_db():
    Cluster.query.update({'main_article_id': None})
    for table in Tag, Article, Cluster, Feed, Icon, Category, User:
        table.query.delete()
    ucontr = UserController()
    ccontr = CategoryController()
    fcontr = FeedController()
    acontr = ArticleController()
    ccontr = CategoryController()
    ucontr.create(**{'is_admin': True, 'is_api': True,
                     'login': 'admin', 'password': 'admin'})
    user1, user2 = [ucontr.create(login=name, email="%s@test.te" % name,
                                  password=name)
                    for name in ["user1", "user2"]]
    now = utc_now()

    for k in range(2):
        article_total = 0

        def to_name(u, cat=None, feed=None, art=None, *args):
            string = "i%d %s" % (k, u.login)
            if cat:
                string += " cat%s" % cat
            if feed is not None:
                string += " feed%s" % feed
            if art is not None:
                string += " art%s" % art
            return string + ''.join(args)
        for user in (user1, user2):
            for i in range(3):
                cat_id = None
                if i:
                    cat_id = ccontr.create(user_id=user.id,
                                        name=to_name(user, i)).id
                feed = fcontr.create(link="feed%d%d" % (k, i), user_id=user.id,
                                     category_id=cat_id,
                                     title=to_name(user, i, i))
                for j in range(3):
                    entry = to_name(user, i, i, j)
                    article_total += 1
                    acontr.create(entry_id=entry,
                            link='http://test.te/%d' % article_total,
                            feed_id=feed.id, user_id=user.id,
                            tags=[to_name(user, i, i, j, '1'),
                                  to_name(user, i, i, j, '2')],
                            category_id=cat_id, title=entry,
                            date=now + timedelta(seconds=k),
                            content="content %d" % article_total)
