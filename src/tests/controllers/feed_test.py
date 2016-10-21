from tests.base import BaseJarrTest
from web.controllers import (ArticleController, ClusterController,
                             FeedController, UserController)


class FeedControllerTest(BaseJarrTest):
    _contr_cls = FeedController

    def test_delete(self):
        feed_ctrl = FeedController()
        for feed in feed_ctrl.read():
            feed_ctrl.delete(feed.id)
        self.assertEquals(0, ClusterController(2).read().count())
        self.assertEquals(0, ArticleController(2).read().count())

    def test_delete_main_cluster_handling(self):
        clu = ClusterController().get(id=10)
        old_title = clu.main_title
        old_feed_title, old_art_id = clu.main_feed_title, clu.main_article_id
        self.assertEquals(2, len(clu.articles))
        FeedController(clu.user_id).delete(clu.main_article.feed_id)
        new_cluster = ClusterController(clu.user_id).get(id=clu.id)
        self.assertEquals(1, len(new_cluster.articles))
        self.assertNotEquals(old_title, new_cluster.main_title)
        self.assertNotEquals(old_feed_title, new_cluster.main_feed_title)
        self.assertNotEquals(old_art_id, new_cluster.main_article_id)

    def test_delete_cluster_handling(self):
        clu = ClusterController().get(id=10)
        old_title = clu.main_title
        old_feed_title, old_art_id = clu.main_feed_title, clu.main_article_id
        self.assertEquals(2, len(clu.articles))
        FeedController(clu.user_id).delete(  # deleting not main article
                next(art.feed_id for art in clu.articles
                     if art.id != clu.main_article_id))
        new_cluster = ClusterController(clu.user_id).get(id=clu.id)
        self.assertEquals(1, len(new_cluster.articles))
        self.assertEquals(old_title, new_cluster.main_title)
        self.assertEquals(old_feed_title, new_cluster.main_feed_title)
        self.assertEquals(old_art_id, new_cluster.main_article_id)

    def test_feed_rights(self):
        feed = FeedController(2).read()[0].dump()
        self.assertTrue(3,
                ArticleController().read(feed_id=feed['id']).count())
        self._test_controller_rights(feed,
                UserController().get(id=feed['user_id']))

    def test_update_cluster_on_change_title(self):
        feed = FeedController(2).read()[0]
        for cluster in feed.clusters:
            self.assertEquals(feed['title'], cluster['main_feed_title'])
        FeedController(2).update({'id': feed.id}, {'title': 'updated title'})

        feed = FeedController(2).get(id=feed.id)
        self.assertEquals('updated title', feed.title)
        for cluster in feed.clusters:
            self.assertEquals(feed.title, cluster.main_feed_title)

    def test_admin_update_cluster_on_change_title(self):
        feed = FeedController(2).read()[0]
        for cluster in feed.clusters:
            self.assertEquals(feed['title'], cluster['main_feed_title'])
        FeedController().update({'id': feed.id}, {'title': 'updated title'})

        feed = FeedController().get(id=feed.id)
        self.assertEquals('updated title', feed.title)
        for cluster in feed.clusters:
            self.assertEquals(feed.title, cluster.main_feed_title)
