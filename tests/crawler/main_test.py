from datetime import datetime, timezone

from mock import patch

from jarr.controllers import FeedController, UserController
from jarr.crawler.main import scheduler
from jarr.lib.utils import utc_now
from tests.base import BaseJarrTest


class CrawlerMainTest(BaseJarrTest):

    def setUp(self):
        super().setUp()
        self._clusteriser_patch = patch('jarr.crawler.main.clusterizer')
        self._sched_async = patch('jarr.crawler.main.scheduler.apply_async')
        self._process_feed_patch = patch('jarr.crawler.main.process_feed')
        self._feed_cleaner_patch = patch('jarr.crawler.main.feed_cleaner')
        self._metrics = [patch(f"jarr.crawler.main.{path}")
                         for path in ['metrics_users_any',
                                      'metrics_users_active',
                                      'metrics_users_long_term',
                                      'metrics_articles_unclustered']]
        self.clusteriser_patch = self._clusteriser_patch.start()
        self.process_feed_patch = self._process_feed_patch.start()
        self.feed_cleaner_patch = self._feed_cleaner_patch.start()
        self.scheduler_patch = self._sched_async.start()
        for metrics_patch in self._metrics:
            metrics_patch.start()

    def tearDown(self):
        self._clusteriser_patch.stop()
        self._process_feed_patch.stop()
        self._feed_cleaner_patch.stop()
        self._sched_async.stop()
        for metrics_patch in self._metrics:
            metrics_patch.stop()

    def test_scheduler(self):
        scheduler()
        UserController().update({}, {'last_connection': utc_now()})
        fctrl = FeedController()

        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(fctrl.read().count(),
                         self.process_feed_patch.apply_async.call_count)
        self.assertEqual(0, self.clusteriser_patch.apply_async.call_count)
        self.assertEqual(0, self.feed_cleaner_patch.apply_async.call_count)
        feed1, feed2, feed3 = list(FeedController().read().limit(3))
        FeedController().update({'id__in': [feed1.id, feed3.id]},
                                {'status': 'to_delete'})
        FeedController().update({'id': feed2.id},
                                {'last_retrieved': epoch, 'expires': epoch})
        self.assertEqual(1, len(list(fctrl.list_fetchable())))
        scheduler()
        self.assertEqual(fctrl.read().count(),
                         self.process_feed_patch.apply_async.call_count)
        self.assertEqual(0, self.clusteriser_patch.apply_async.call_count)
        self.assertEqual(2, self.feed_cleaner_patch.apply_async.call_count)
