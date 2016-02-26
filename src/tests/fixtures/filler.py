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

    article_total = 0
    for user in (user1, user2):
        for i in range(3):
            cat_id = None
            if i:
                cat_id = ccontr.create(user_id=user.id,
                                       name="category%d" % i).id
            feed = fcontr.create(link="feed%d" % i, user_id=user.id,
                                    category_id=cat_id,
                                    title="%s feed%d" % (user.login, i))
            for j in range(3):
                entry = "%s %s article%d" % (user.login, feed.title, j)
                article_total += 1
                acontr.create(entry_id=entry,
                        link='http://test.te/%d' % article_total,
                        feed_id=feed.id, user_id=user.id, category_id=cat_id,
                        title=entry, content="content %d" % article_total)

def reset_db():
    db_empty()
