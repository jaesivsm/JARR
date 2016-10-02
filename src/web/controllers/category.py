from .abstract import AbstractController
from web.models import Category
from .feed import FeedController


class CategoryController(AbstractController):
    _db_cls = Category
