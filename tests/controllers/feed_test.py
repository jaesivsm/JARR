from datetime import datetime, timedelta, timezone

from jarr.bootstrap import conf, session
from jarr.controllers import (ArticleController, ClusterController,
                              FeedController, UserController)
from jarr.lib.utils import utc_now
from tests.base import BaseJarrTest
from tests.utils import update_on_all_objs


class FeedControllerTest(BaseJarrTest):
    _contr_cls = FeedController

    def test_delete(self):
        feed_ctrl = FeedController()
        for feed in feed_ctrl.read():
            feed_ctrl.delete(feed.id)
        self.assertEqual(0, ClusterController(2).read().count())
        self.assertEqual(0, ArticleController(2).read().count())

    def test_delete_main_cluster_handling(self):
        suffix = 'suffix'
        clu = ClusterController().get(id=10)
        acontr = ArticleController(clu.user_id)
        fcontr = FeedController(clu.user_id)
        old_title = clu.main_title
        old_feed_title, old_art_id = clu.main_feed_title, clu.main_article_id
        for art_to_del in acontr.read(link=clu.main_article.link,
                                      id__ne=clu.main_article.id):
            acontr.delete(art_to_del.id)

        other_feed = fcontr.read(id__ne=clu.main_article.feed_id).first()
        update_on_all_objs(articles=[clu.main_article], feeds=[other_feed],
                cluster_enabled=True)
        acontr.create(
                feed_id=other_feed.id,
                entry_id=clu.main_article.entry_id + suffix,
                link=clu.main_article.link,
                title=clu.main_article.title + suffix,
                content=clu.main_article.content + suffix,
                date=clu.main_article.date + timedelta(1),
                retrieved_date=clu.main_article.retrieved_date + timedelta(1),
        )

        ClusterController(clu.user_id).clusterize_pending_articles()
        clu = ClusterController().get(id=10)
        self.assertEqual(2, len(clu.articles))
        fcontr.delete(clu.main_article.feed_id)
        new_cluster = ClusterController(clu.user_id).get(id=clu.id)
        self.assertEqual(1, len(new_cluster.articles))
        self.assertNotEqual(old_title, new_cluster.main_title)
        self.assertNotEqual(old_feed_title, new_cluster.main_feed_title)
        self.assertNotEqual(old_art_id, new_cluster.main_article_id)

    def test_delete_cluster_handling(self):
        clu = ClusterController().get(id=10)
        old_title = clu.main_title
        old_feed_title, old_art_id = clu.main_feed_title, clu.main_article_id
        self.assertEqual(1, len(clu.articles))
        new_cluster = ClusterController(clu.user_id).get(id=clu.id)
        self.assertEqual(1, len(new_cluster.articles))
        self.assertEqual(old_title, new_cluster.main_title)
        self.assertEqual(old_feed_title, new_cluster.main_feed_title)
        self.assertEqual(old_art_id, new_cluster.main_article_id)

    def test_feed_rights(self):
        feed = FeedController(2).read()[0]
        self.assertEqual(3,
                ArticleController().read(feed_id=feed.id).count())
        self._test_controller_rights(feed,
                UserController().get(id=feed.user_id))

    def test_update_cluster_on_change_title(self):
        feed = ClusterController(2).read()[0].main_article.feed
        for cluster in feed.clusters:
            self.assertEqual(feed.title, cluster.main_feed_title)
        FeedController(2).update({'id': feed.id}, {'title': 'updated title'})

        feed = FeedController(2).get(id=feed.id)
        self.assertEqual('updated title', feed.title)
        for cluster in feed.clusters:
            self.assertEqual(feed.title, cluster.main_feed_title)

    def test_admin_update_cluster_on_change_title(self):
        feed = ClusterController(2).read()[0].main_article.feed
        for cluster in feed.clusters:
            self.assertEqual(feed.title, cluster.main_feed_title)
        FeedController().update({'id': feed.id}, {'title': 'updated title'})

        feed = FeedController().get(id=feed.id)
        self.assertEqual('updated title', feed.title)
        for cluster in feed.clusters:
            self.assertEqual(feed.title, cluster.main_feed_title)

    def assert_late_count(self, count, msg):
        fctrl = FeedController()
        self.assertEqual(count, len(list(fctrl.list_late())), msg)
        self.assertEqual(count, len(fctrl.list_fetchable()), msg)

    @staticmethod
    def update_all_no_ctrl(**kwargs):
        for feed in FeedController().read():
            for key, value in kwargs.items():
                setattr(feed, key, value)
            session.add(feed)
        session.commit()

    def assert_in_range(self, low, val, high):
        self.assertTrue(low <= val,
                        "%s > %s" % (low.isoformat(), val.isoformat()))
        self.assertTrue(val <= high,
                        "%s > %s" % (val.isoformat(), high.isoformat()))

    def test_fetchable(self):
        fctrl = FeedController()
        total = fctrl.read().count()
        unix = datetime(1970, 1, 1).replace(tzinfo=timezone.utc)
        count = 0
        for fd in fctrl.list_late():
            count += 1
            self.assertEqual(unix, fd.last_retrieved)
            self.assertEqual(unix, fd.expires)
        self.assertEqual(total, count)

        fetchables = fctrl.list_fetchable()
        now = utc_now()
        for fd in fetchables:
            self.assert_in_range(now - timedelta(seconds=1),
                                 fd.last_retrieved, now)
            self.assertEqual(unix, fd.expires)
        self.assert_late_count(0,
                "no late feed to report because all just fetched")
        fctrl.update({}, {'expires': unix})
        now = utc_now()
        for fd in fctrl.read():  # expires should be corrected
            self.assert_in_range(
                    now + timedelta(seconds=conf.feed.min_expires - 1),
                    fd.expires,
                    now + timedelta(seconds=conf.feed.min_expires + 1))

        lr_not_matter = timedelta(seconds=conf.feed.min_expires + 10)
        self.update_all_no_ctrl(expires=utc_now() - timedelta(seconds=1),
                                last_retrieved=utc_now() - lr_not_matter)
        self.assert_late_count(total, "all feed just expired")
        self.update_all_no_ctrl(expires=utc_now() + timedelta(seconds=1))
        self.assert_late_count(0,
                "all feed will expire in a second, none are expired")


    def _test_fetching_anti_herding_mech(self, now):
        fctrl = FeedController()
        total = fctrl.read().count()

        half = timedelta(seconds=conf.feed.min_expires / 2)
        twice = timedelta(seconds=conf.feed.min_expires * 2)
        long_ago = timedelta(seconds=conf.feed.max_expires * 2)

        self.update_all_no_ctrl(expires=now + half, last_retrieved=now)
        self.assert_late_count(0, "all have just been retrieved, none expired")
        self.update_all_no_ctrl(expires=now - twice, last_retrieved=now - half)
        self.assert_late_count(0, "have been retrieved not too long ago")

        self.update_all_no_ctrl(expires=now + twice,
                                last_retrieved=now - long_ago)
        self.assert_late_count(total,
                               "all retrieved some time ago, not expired")

    def test_fetching_anti_herding_mech_utctimezone(self):
        self._test_fetching_anti_herding_mech(utc_now())

    def test_fetching_anti_herding_mech_utcplustwelve(self):
        self._test_fetching_anti_herding_mech(
                utc_now().astimezone(timezone(timedelta(hours=12))))
