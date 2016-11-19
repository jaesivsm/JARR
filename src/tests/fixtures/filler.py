from datetime import timedelta

from lib.utils import utc_now
from manager import db_create, db_empty
from web.controllers import (ArticleController, CategoryController,
                             FeedController, UserController)


def populate_db():
    db_create()
    ucontr = UserController()
    ccontr = CategoryController()
    fcontr = FeedController()
    acontr = ArticleController()
    ccontr = CategoryController()
    user1, user2 = [ucontr.create(login=name, email="%s@test.te" % name,
                                  password=name)
                    for name in ["user1", "user2"]]
    now = utc_now()

    for k in range(2):
        article_total = 0

        def to_name(u, c=None, f=None, a=None, *args):
            string = "i%d %s" % (k, u.login)
            if c:
                string += " cat%s" % c
            if f is not None:
                string += " feed%s" % f
            if a is not None:
                string += " art%s" % a
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

def reset_db():
    db_empty()
