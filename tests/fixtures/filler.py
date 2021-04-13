from datetime import timedelta

from jarr.lib.utils import utc_now
from jarr.bootstrap import session
from jarr.controllers import (ArticleController, CategoryController,
                              ClusterController,
                              FeedController, UserController)


def to_name(user, iter_, cat=None, feed=None, art=None, arg=''):
    string = "i%d %s" % (iter_, user.login)
    if cat:
        string += " cat%s" % cat
    if feed is not None:
        string += " feed%s" % feed
    if art is not None:
        string += " art%s" % art
    return string + arg


def populate_db():
    fcontr = FeedController()
    ccontr = CategoryController()
    uctrl = UserController()
    uctrl.create(is_admin=True, is_api=True, cluster_enabled=False,
                 login='admin', password='admin')
    user1, user2 = [uctrl.create(login=name, cluster_enabled=False,
                                 email="%s@test.te" % name, password=name)
                    for name in ["user1", "user2"]]

    for iteration in range(2):
        article_total = 0

        for user in (user1, user2):
            for iter_cat in range(3):
                cat_id = None
                if iter_cat:
                    cat_id = ccontr.create(
                        user_id=user.id,
                        name=to_name(user, iteration, iter_cat)).id
                feed_id = fcontr.create(
                    link="feed%d%d" % (iteration, iter_cat),
                    user_id=user.id, category_id=cat_id,
                    title=to_name(user, iteration, iter_cat, iter_cat)).id
                for iter_art in range(3):
                    entry = to_name(user, iteration,
                                    iter_cat, iter_cat, iter_art)

                    tags = [to_name(user, iteration, iter_cat, iter_cat,
                            iter_art, str(i)) for i in range(2)]
                    article_total += 1
                    ArticleController().create(
                        entry_id=entry, feed_id=feed_id, user_id=user.id,
                        tags=tags, category_id=cat_id, title=entry,
                        link='http://test.te/%d' % article_total,
                        date=utc_now() + timedelta(seconds=iteration),
                        content="content %d" % article_total)

    session.commit()
    session.flush()
    ClusterController().clusterize_pending_articles()
