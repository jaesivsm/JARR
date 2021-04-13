from jarr.controllers import CategoryController, FeedController, UserController


def update_on_all_objs(articles=None, feeds=None, categories=None, users=None,
                       **kwargs):
    articles = articles or []
    feeds = feeds or []
    categories = categories or []
    users = users or []
    feed_ids = {a.feed_id for a in articles}.union({f.id for f in feeds})
    category_ids = {a.category_id for a in articles if a.category_id}\
        .union({f.category_id for f in feeds if f.category_id})\
        .union({c.id for c in categories})

    user_ids = {a.user_id for a in articles}\
        .union({f.user_id for f in feeds})\
        .union({c.user_id for c in categories})\
        .union({u.id for u in users})
    FeedController().update({'__or__': [{'id__in': feed_ids},
                                        {'category_id__in': category_ids},
                                        {'user_id__in': user_ids}]}, kwargs)
    CategoryController().update(
        {'__or__': [{'id__in': category_ids},
                    {'user_id__in': user_ids}]}, kwargs)
    UserController().update(
        {'id__in': user_ids},
        # pushing default to user if not specifically false
        {k: v if v is not None else True for k, v in kwargs.items()})
