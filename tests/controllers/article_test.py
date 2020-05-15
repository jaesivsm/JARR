from tests.base import BaseJarrTest
from jarr.controllers import (ArticleController, FeedController,
        UserController, ClusterController)

USER_ID = 2

class ArticleControllerTest(BaseJarrTest):
    _contr_cls = ArticleController

    def test_article_rights(self):
        article = ArticleController(USER_ID).read().first()
        self._test_controller_rights(article,
                UserController().get(id=article.user_id))

    def _test_create_using_filters(self):
        # FIXME wait redo filters
        feed_ctr = FeedController(USER_ID)
        acontr = ArticleController(USER_ID)
        feed1, feed2, feed3 = [f for f in feed_ctr.read()][0:3]
        feed_ctr.update({'id': feed3.id},
                        {'cluster_enabled': True,
                         'filters': [{"type": "regex",
                                      "pattern": ".*(pattern1|pattern2).*",
                                      "action on": "no match",
                                      "action": "mark as favorite"},
                                     {"type": "simple match",
                                      "pattern": "pattern3",
                                      "action on": "match",
                                      "action": "mark as read"}]})
        feed_ctr.update({'id': feed1.id},
                        {'filters': [{"type": "simple match",
                                      "pattern": "pattern3",
                                      "action on": "match",
                                      "action": "mark as read"}]})
        feed_ctr.update({'id': feed2.id},
                        {'filters': [{"type": "tag match",
                                      "pattern": "pattern4",
                                      "action on": "match",
                                      "action": "skipped"},
                                     {"type": "tag contains",
                                      "pattern": "pattern5",
                                      "action on": "match",
                                      "action": "skipped"}]})

        art1 = acontr.create(
                entry_id="will be read and faved 1",
                feed_id=feed1.id,
                title="garbage pattern1 pattern3 garbage",
                content="doesn't matter",
                link="cluster1")

        art2 = acontr.create(
                entry_id="will be ignored 2",
                feed_id=feed1.id,
                title="garbage see pattern garbage",
                content="doesn't matter2",
                link="is ignored 2")

        art3 = acontr.create(
                entry_id="will be read 3",
                user_id=2,
                feed_id=feed2.id,
                title="garbage pattern3 garbage",
                content="doesn't matter",
                link="doesn't matter either3")

        art4 = acontr.create(
                entry_id="will be ignored 4",
                user_id=2,
                feed_id=feed2.id,
                title="garbage see pattern garbage",
                content="doesn't matter2",
                link="doesn't matter either4")

        art5 = acontr.create(
                entry_id="will be faved 5",
                feed_id=feed3.id,
                title="garbage anti-attern3 garbage",
                content="doesn't matter",
                link="cluster1")
        art6 = acontr.create(
                entry_id="will be faved 6",
                feed_id=feed3.id,
                title="garbage pattern1 garbage",
                content="doesn't matter2",
                link="doesn't matter 6")
        art7 = acontr.create(
                entry_id="will be read 7",
                feed_id=feed3.id,
                title="garbage pattern3 garbage",
                content="doesn't matter3",
                link="doesn't matter either7")

        art8 = acontr.create(
                entry_id="will be ignored",
                feed_id=feed3.id,
                title="garbage pattern4 garbage",
                content="doesn't matter4-matter4_matter4",
                lang='fa_ke',
                link="doesn't matter either8")

        art9 = acontr.create(
                entry_id="unique9",
                feed_id=feed2.id,
                title="garbage", tags=['garbage', 'pattern4'],
                content="doesn't matterç",
                link="doesn't matter either9")

        art10 = acontr.create(
                entry_id="will be ignored",
                feed_id=feed2.id,
                title="garbage", tags=['pattern5 garbage', 'garbage'],
                content="doesn't matter10",
                link="doesn't matter either10")

        ClusterController(USER_ID).clusterize_pending_articles()

        self.assertTrue(acontr.get(id=art1.id).cluster.read)
        self.assertFalse(acontr.get(id=art1.id).cluster.liked)
        self.assertFalse(acontr.get(id=art2.id).cluster.read)
        self.assertFalse(acontr.get(id=art2.id).cluster.liked)
        self.assertFalse(acontr.get(id=art3.id).cluster.read)
        self.assertFalse(acontr.get(id=art3.id).cluster.liked)
        self.assertFalse(acontr.get(id=art4.id).cluster.read)
        self.assertFalse(acontr.get(id=art4.id).cluster.liked)
        self.assertTrue(art5.cluster.read,
                "should be read because it clustered")
        self.assertTrue(art5.cluster.liked)
        self.assertFalse(art6.cluster.read)
        self.assertFalse(art6.cluster.liked)
        self.assertTrue(art7.cluster.read)
        self.assertTrue(art7.cluster.liked)
        self.assertFalse(art8.cluster.read)
        self.assertTrue(art8.cluster.liked)
        self.assertIsNone(art9)
        self.assertEqual(0, acontr.read(entry_id='unique9').count())
        self.assertIsNone(art10)
        self.assertEqual(0, acontr.read(entry_id='unique10').count())
