from datetime import timedelta

from jarr_common.utils import utc_now
from jarr.bootstrap import conf
from jarr.controllers import (ArticleController, CategoryController,
                              FeedController, UserController)


def to_name(user, iter_, cat=None, feed=None, art=None, *args):
    string = "i%d %s" % (iter_, user.login)
    if cat:
        string += " cat%s" % cat
    if feed is not None:
        string += " feed%s" % feed
    if art is not None:
        string += " art%s" % art
    return string + ''.join(args)


def populate_db():
    ucontr = UserController()
    ccontr = CategoryController()
    fcontr = FeedController()
    acontr = ArticleController()
    ccontr = CategoryController()
    ucontr.create(**{'is_admin': True, 'is_api': True,
                     'login': conf.crawler.login,
                     'password': conf.crawler.passwd})
    user1, user2 = [ucontr.create(login=name, email="%s@test.te" % name,
                                  password=name)
                    for name in ["user1", "user2"]]
    now = utc_now()

    for iteration in range(2):
        article_total = 0

        for user in (user1, user2):
            for iter_cat in range(3):
                cat_id = None
                if iter_cat:
                    cat_id = ccontr.create(user_id=user.id,
                                           name=to_name(user, iteration,
                                                        iter_cat)).id
                feed = fcontr.create(link="feed%d%d" % (iteration, iter_cat),
                                     user_id=user.id, category_id=cat_id,
                                     title=to_name(user, iteration,
                                                   iter_cat, iter_cat))
                for iter_art in range(3):
                    entry = to_name(user, iteration,
                                    iter_cat, iter_cat, iter_art)

                    tags = [to_name(user, iteration, iter_cat, iter_cat,
                            iter_art, str(i)) for i in range(2)]
                    article_total += 1
                    acontr.create(entry_id=entry,
                            link='http://test.te/%d' % article_total,
                            feed_id=feed.id, user_id=user.id, tags=tags,
                            category_id=cat_id, title=entry,
                            date=now + timedelta(seconds=iteration),
                            content="content %d" % article_total)
