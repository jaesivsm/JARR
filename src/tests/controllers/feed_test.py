from tests.base import BaseJarrTest
from web.controllers import (UserController, FeedController,
                             ArticleController, ClusterController)


class FeedControllerTest(BaseJarrTest):
    _contr_cls = FeedController

    def test_delete(self):
        feed_ctrl = FeedController()
        for feed in feed_ctrl.read():
            feed_ctrl.delete(feed.id)
        self.assertEquals(0, ClusterController(2).read().count())
        self.assertEquals(0, ArticleController(2).read().count())

    def test_feed_rights(self):
        feed = FeedController(2).read()[0].dump()
        self.assertTrue(3,
                ArticleController().read(feed_id=feed['id']).count())
        self._test_controller_rights(feed,
                UserController().get(id=feed['user_id']))
