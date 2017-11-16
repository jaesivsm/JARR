from tests.base import BaseJarrTest
from datetime import datetime, timedelta, timezone
from bootstrap import conf
from lib.utils import utc_now
from web.controllers import (ArticleController, ClusterController,
                             FeedController, UserController)


class FeedControllerTest(BaseJarrTest):
    _contr_cls = FeedController

    def test_delete(self):
        feed_ctrl = FeedController()
        for feed in feed_ctrl.read():
            feed_ctrl.delete(feed.id)
        self.assertEqual(0, ClusterController(2).read().count())
        self.assertEqual(0, ArticleController(2).read().count())

    def test_delete_main_cluster_handling(self):
        clu = ClusterController().get(id=10)
        old_title = clu.main_title
        old_feed_title, old_art_id = clu.main_feed_title, clu.main_article_id
        self.assertEqual(2, len(clu.articles))
        FeedController(clu.user_id).delete(clu.main_article.feed_id)
        new_cluster = ClusterController(clu.user_id).get(id=clu.id)
        self.assertEqual(1, len(new_cluster.articles))
        self.assertNotEqual(old_title, new_cluster.main_title)
        self.assertNotEqual(old_feed_title, new_cluster.main_feed_title)
        self.assertNotEqual(old_art_id, new_cluster.main_article_id)

    def test_delete_cluster_handling(self):
        clu = ClusterController().get(id=10)
        old_title = clu.main_title
        old_feed_title, old_art_id = clu.main_feed_title, clu.main_article_id
        self.assertEqual(2, len(clu.articles))
        FeedController(clu.user_id).delete(  # deleting not main article
                next(art.feed_id for art in clu.articles
                     if art.id != clu.main_article_id))
        new_cluster = ClusterController(clu.user_id).get(id=clu.id)
        self.assertEqual(1, len(new_cluster.articles))
        self.assertEqual(old_title, new_cluster.main_title)
        self.assertEqual(old_feed_title, new_cluster.main_feed_title)
        self.assertEqual(old_art_id, new_cluster.main_article_id)

    def test_feed_rights(self):
        feed = FeedController(2).read()[0].dump()
        self.assertTrue(3,
                ArticleController().read(feed_id=feed['id']).count())
        self._test_controller_rights(feed,
                UserController().get(id=feed['user_id']))

    def test_update_cluster_on_change_title(self):
        feed = FeedController(2).read()[0]
        for cluster in feed.clusters:
            self.assertEqual(feed['title'], cluster['main_feed_title'])
        FeedController(2).update({'id': feed.id}, {'title': 'updated title'})

        feed = FeedController(2).get(id=feed.id)
        self.assertEqual('updated title', feed.title)
        for cluster in feed.clusters:
            self.assertEqual(feed.title, cluster.main_feed_title)

    def test_admin_update_cluster_on_change_title(self):
        feed = FeedController(2).read()[0]
        for cluster in feed.clusters:
            self.assertEqual(feed['title'], cluster['main_feed_title'])
        FeedController().update({'id': feed.id}, {'title': 'updated title'})

        feed = FeedController().get(id=feed.id)
        self.assertEqual('updated title', feed.title)
        for cluster in feed.clusters:
            self.assertEqual(feed.title, cluster.main_feed_title)

    def assert_late_count(self, count, msg):
        fctrl = FeedController()
        self.assertEqual(count, len(list(fctrl.list_late())), msg)
        self.assertEqual(count, len(fctrl.list_fetchable()), msg)

    def test_fetchable(self):
        fctrl = FeedController()
        total = fctrl.read().count()
        unix = datetime(1970, 1, 1).replace(tzinfo=timezone.utc)

        def assert_in_range(low, val, high):
            assert low <= val, "%s > %s" % (low.isoformat(), val.isoformat())
            assert val <= high, "%s > %s" % (val.isoformat(), high.isoformat())

        def reset_all_last_retrieved():
            last = utc_now() - timedelta(seconds=conf.FEED_MIN_EXPIRES)
            fctrl.update({}, {'last_retrieved': last})

        count = 0
        for fd in fctrl.list_late():
            count += 1
            self.assertEqual(unix, fd.last_retrieved)
            self.assertEqual(unix, fd.expires)
        self.assertEqual(total, count)

        fetchables = fctrl.list_fetchable()
        now = utc_now()
        for fd in fetchables:
            assert_in_range(now - timedelta(seconds=1), fd.last_retrieved, now)
            self.assertEqual(unix, fd.expires)
        self.assert_late_count(0,
                "no late feed to report because all just fetched")

        reset_all_last_retrieved()
        self.assert_late_count(total,
                "all last_retr and expires at unix time, all feed to fetch")
        reset_all_last_retrieved()
        fctrl.update({}, {'expires': utc_now() - timedelta(seconds=1)})
        self.assert_late_count(total, "all feed just expired")
        fctrl.update({}, {'expires': utc_now() + timedelta(seconds=1)})
        self.assert_late_count(0,
                "all feed will expire in a second, none are expired")

        reset_all_last_retrieved()
        fctrl.update({}, {'expires': utc_now() + timedelta(seconds=1)})
        self.assert_late_count(0,
                "all feed will expire in a second, none are expired")

    def _test_fetching_anti_herding_mech(self, now):
        fctrl = FeedController()
        total = fctrl.read().count()
        unix = datetime(1970, 1, 1, tzinfo=timezone.utc)

        half = timedelta(seconds=conf.FEED_MIN_EXPIRES / 2)
        twice = timedelta(seconds=conf.FEED_MIN_EXPIRES * 2)

        fctrl.update({}, {'expires': unix, 'last_retrieved': now + half})
        self.assert_late_count(0, "all have just been retrieved, none expired")
        fctrl.update({}, {'expires': unix, 'last_retrieved': now - half})
        self.assert_late_count(0, "all have just been retrieved, none expired")

        fctrl.update({}, {'expires': unix, 'last_retrieved': now + twice})
        self.assert_late_count(total,
                "all retrieved some time ago, all expired")
        fctrl.update({}, {'expires': unix, 'last_retrieved': now - twice})
        self.assert_late_count(total,
                "all retrieved some time ago, all expired")

    def test_fetching_anti_herding_mech_utctimezone(self):
        self._test_fetching_anti_herding_mech(utc_now())

    def test_fetching_anti_herding_mech_utcplustwelve(self):
        self._test_fetching_anti_herding_mech(
                utc_now().astimezone(timezone(timedelta(hours=12))))
