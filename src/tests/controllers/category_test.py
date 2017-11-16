from tests.base import BaseJarrTest
from web.controllers import (ArticleController, CategoryController,
                             FeedController, UserController)


class CategoryControllerTest(BaseJarrTest):
    _contr_cls = CategoryController

    def test_feed_rights(self):
        cat = CategoryController(2).read()[0].dump()
        self.assertTrue(3,
                ArticleController().read(category_id=cat['id']).count())
        self.assertTrue(3,
                FeedController().read(category_id=cat['id']).count())
        self._test_controller_rights(cat,
                UserController().get(id=cat['user_id']))

    def test_feed_and_article_deletion(self):
        ccontr = CategoryController(2)
        cat = ccontr.read()[0].dump()
        ccontr.delete(cat['id'])
        self.assertEqual(0,
                ArticleController().read(category_id=cat['id']).count())
        self.assertEqual(0,
                FeedController().read(category_id=cat['id']).count())
