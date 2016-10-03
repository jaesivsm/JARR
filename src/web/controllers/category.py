from .abstract import AbstractController
from web.models import Category


class CategoryController(AbstractController):
    _db_cls = Category
