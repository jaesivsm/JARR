import json

from tests.base import JarrFlaskCommon
from tests.utils import update_on_all_objs
from jarr.controllers import (UserController, ClusterController,
        FeedController, ArticleController)


class OnePageAppTest(JarrFlaskCommon):

    def setUp(self):
        super().setUp()
        self.user = UserController().get(id=2)

    def assertClusterCount(self, count, filters=None):
        filters = filters or {}
        resp = self.jarr_client('get', 'middle_panel',
                data=filters, user=self.user.login)
        self.assertStatusCode(200, resp)
        clusters = resp.json()
        self.assertEqual(count, len(clusters))
        return clusters

    def test_middle_panel(self):
        clusters = self.assertClusterCount(18)
        self.assertClusterCount(18, {'filter': 'unread'})
        self.assertClusterCount(0, {'filter': 'liked'})
        self.jarr_client('put', 'cluster', clusters[0]['id'],
                  data={'liked': True}, user=self.user.login)
        self.assertClusterCount(1, {'filter': 'liked'})
        self.assertClusterCount(3, {'feed_id': 1})
        self.assertClusterCount(3, {'feed_id': 2})
        self.assertClusterCount(3, {'category_id': 1})
        self.assertClusterCount(6, {'category_id': 0})

    def test_search(self):
        self.assertClusterCount(0, {'search_str': 'test'})
        self.assertClusterCount(18, {'search_str': 'user1'})
        self.assertClusterCount(6,
                {'search_str': 'feed1', 'search_title': True})
        self.assertClusterCount(6,
                {'search_str': 'user1 feed0', 'search_content': True})
        self.assertClusterCount(2,
                {'search_str': 'content 3', 'search_title': True,
                 'search_content': True})

    def test_middle_panel_filtered_on_category(self):
        cat_id = self.user.categories[0].id
        clusters = self.assertClusterCount(3,
                {'category_id': cat_id})
        for cluster in clusters:
            self.assertIn(cat_id, cluster['categories_id'])

    def test_middle_panel_filtered_on_feed(self):
        feed_id = self.user.feeds[0].id
        clusters = self.assertClusterCount(3, {'feed_id': feed_id})
        for cluster in clusters:
            self.assertIn(feed_id, cluster['feeds_id'])

    def _mark_as_read(self, read_count, filters=None):
        filters = filters or {}
        resp = self.jarr_client('put', 'mark_all_as_read', data=filters,
                user=self.user.login)
        self.assertStatusCode(200, resp)
        self.assertEqual(read_count, len(json.loads(resp.data.decode('utf8'))))

    def test_MarkClustersAsRead_put(self):
        self.assertClusterCount(18, {'filter': 'unread'})
        self._mark_as_read(0, {'filter': 'liked'})
        self.assertClusterCount(18, {'filter': 'unread'})
        self._mark_as_read(18, {'filter': 'unread'})
        self.assertClusterCount(0, {'filter': 'unread'})

    def test_MarkClustersAsRead_put_only_singles(self):
        feed = FeedController(self.user.id).read()[0]
        update_on_all_objs(feeds=[feed],
                cluster_same_feed=True, cluster_enabled=True)
        # creating a new article that will cluster
        ArticleController(self.user.id).create(entry_id='new entry_id',
                title='new title', content='new content',
                feed_id=feed.id, link=feed.articles[0].link)
        ClusterController.clusterize_pending_articles()
        self.assertClusterCount(18, {'filter': 'unread'})
        self._mark_as_read(17, {'only_singles': True, 'filter': 'unread'})
        self.assertClusterCount(1, {'filter': 'unread'})

    def test_MarkClustersAsRead_put_one_feed(self):
        self.assertClusterCount(18, {'filter': 'unread'})
        self._mark_as_read(3, {'filter': 'unread', 'feed_id': 1})
        self.assertClusterCount(15, {'filter': 'unread'})

    def test_MarkClustersAsRead_put_one_category(self):
        self.assertClusterCount(18, {'filter': 'unread'})
        self._mark_as_read(3, {'filter': 'unread', 'category_id': 1})
        self.assertClusterCount(15, {'filter': 'unread'})

    def test_MarkClustersAsRead_put_null_category(self):
        self.assertClusterCount(18, {'filter': 'unread'})
        self._mark_as_read(6, {'filter': 'unread', 'category_id': 0})
        self.assertClusterCount(12, {'filter': 'unread'})
