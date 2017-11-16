from tests.base import BaseJarrTest
from web.controllers import ArticleController, FeedController, UserController


class ArticleControllerTest(BaseJarrTest):
    _contr_cls = ArticleController

    def test_article_rights(self):
        article = ArticleController(2).read()[0].dump()
        self._test_controller_rights(article,
                UserController().get(id=article['user_id']))

    def test_create_using_filters(self):
        feed_ctr = FeedController(2)
        feed1 = feed_ctr.read()[0].dump()
        feed2 = feed_ctr.read()[1].dump()
        feed3 = feed_ctr.read()[2].dump()
        feed_ctr.update({'id': feed3['id']},
                        {'filters': [{"type": "regex",
                                      "pattern": ".*(pattern1|pattern2).*",
                                      "action on": "no match",
                                      "action": "mark as favorite"},
                                     {"type": "simple match",
                                      "pattern": "pattern3",
                                      "action on": "match",
                                      "action": "mark as read"}]})
        feed_ctr.update({'id': feed1['id']},
                        {'filters': [{"type": "simple match",
                                      "pattern": "pattern3",
                                      "action on": "match",
                                      "action": "mark as read"}]})
        feed_ctr.update({'id': feed2['id']},
                        {'filters': [{"type": "tag match",
                                      "pattern": "pattern4",
                                      "action on": "match",
                                      "action": "skipped"},
                                     {"type": "tag contains",
                                      "pattern": "pattern5",
                                      "action on": "match",
                                      "action": "skipped"}]})

        art1 = ArticleController(2).create(
                entry_id="will be read and faved 1",
                feed_id=feed1['id'],
                title="garbage pattern1 pattern3 garbage",
                content="doesn't matter",
                link="cluster1")
        self.assertTrue(art1.cluster.read)
        self.assertFalse(art1.cluster.liked)

        art2 = ArticleController(2).create(
                entry_id="will be ignored 2",
                feed_id=feed1['id'],
                title="garbage see pattern garbage",
                content="doesn't matter2",
                link="is ignored 2")
        self.assertFalse(art2.cluster.read)
        self.assertFalse(art2.cluster.liked)

        art3 = ArticleController(2).create(
                entry_id="will be read 3",
                user_id=2,
                feed_id=feed2['id'],
                title="garbage pattern3 garbage",
                content="doesn't matter",
                link="doesn't matter either3")
        self.assertFalse(art3.cluster.read)
        self.assertFalse(art3.cluster.liked)

        art4 = ArticleController(2).create(
                entry_id="will be ignored 4",
                user_id=2,
                feed_id=feed2['id'],
                title="garbage see pattern garbage",
                content="doesn't matter2",
                link="doesn't matter either4")
        self.assertFalse(art4.cluster.read)
        self.assertFalse(art4.cluster.liked)

        art5 = ArticleController(2).create(
                entry_id="will be faved 5",
                feed_id=feed3['id'],
                title="garbage anti-attern3 garbage",
                content="doesn't matter",
                link="cluster1")
        self.assertTrue(art5.cluster.read,
                "should be read because it clustered")
        self.assertTrue(art5.cluster.liked)

        art6 = ArticleController(2).create(
                entry_id="will be faved 6",
                feed_id=feed3['id'],
                title="garbage pattern1 garbage",
                content="doesn't matter2",
                link="doesn't matter 6")
        self.assertFalse(art6.cluster.read)
        self.assertFalse(art6.cluster.liked)

        art7 = ArticleController(2).create(
                entry_id="will be read 7",
                feed_id=feed3['id'],
                title="garbage pattern3 garbage",
                content="doesn't matter3",
                link="doesn't matter either7")
        self.assertTrue(art7.cluster.read)
        self.assertTrue(art7.cluster.liked)

        art8 = ArticleController(2).create(
                entry_id="will be ignored",
                feed_id=feed3['id'],
                title="garbage pattern4 garbage",
                content="doesn't matter4-matter4_matter4",
                lang='fa_ke',
                link="doesn't matter either8")
        self.assertFalse(art8.cluster.read)
        self.assertTrue(art8.cluster.liked)

        art9 = ArticleController(2).create(
                entry_id="unique9",
                feed_id=feed2['id'],
                title="garbage", tags=['garbage', 'pattern4'],
                content="doesn't matterç",
                link="doesn't matter either9")
        self.assertIsNone(art9)
        self.assertEqual(0,
                ArticleController(2).read(entry_id='unique9').count())

        art10 = ArticleController(2).create(
                entry_id="will be ignored",
                feed_id=feed2['id'],
                title="garbage", tags=['pattern5 garbage', 'garbage'],
                content="doesn't matter10",
                link="doesn't matter either10")
        self.assertIsNone(art10)
        self.assertEqual(0,
                ArticleController(2).read(entry_id='unique10').count())
