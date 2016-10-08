from .abstract import AbstractController
from web.models import Category


class CategoryController(AbstractController):
    _db_cls = Category

    def delete(self, obj_id):
        from web.controllers import FeedController
        FeedController(self.user_id).update({'category_id': obj_id},
                                            {'category_id': None},
                                            commit=None)
        return super().delete(obj_id)
