from manager import db_create, db_empty
from web.controllers import UserController, CategoryController, \
                            FeedController, ArticleController


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

    def to_name(u, c=None, f=None, a=None):
        string = u.login
        if c:
            string += " cat%s" % c
        if f is not None:
            string += " feed%s" % f
        if a is not None:
            string += " art%s" % a
        return string

    for _ in range(2):
        article_total = 0
        for user in (user1, user2):
            for i in range(3):
                cat_id = None
                if i:
                    cat_id = ccontr.create(user_id=user.id,
                                        name=to_name(user, i)).id
                feed = fcontr.create(link="feed%d" % i, user_id=user.id,
                                    category_id=cat_id,
                                    title=to_name(user, i, i))
                for j in range(3):
                    entry = to_name(user, i, i, j)
                    article_total += 1
                    acontr.create(entry_id=entry,
                            link='http://test.te/%d' % article_total,
                            feed_id=feed.id, user_id=user.id,
                            category_id=cat_id, title=entry,
                            content="content %d" % article_total)

def reset_db():
    db_empty()
