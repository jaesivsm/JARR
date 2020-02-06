from jarr.models import Category

from .abstract import AbstractController


class CategoryController(AbstractController):
    _db_cls = Category

    def delete(self, obj_id, commit=True):
        from jarr.controllers import FeedController
        FeedController(self.user_id).update({'category_id': obj_id},
                                            {'category_id': None},
                                            commit=None)
        return super().delete(obj_id)
