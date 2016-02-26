from tests.base import BaseJarrTest
from web.controllers import UserController, FeedController, ArticleController


class FeedControllerTest(BaseJarrTest):
    _contr_cls = FeedController

    def test_feed_rights(self):
        feed = FeedController(2).read()[0].dump()
        self.assertTrue(3,
                ArticleController().read(feed_id=feed['id']).count())
        self._test_controller_rights(feed,
                UserController().get(id=feed['user_id']))
