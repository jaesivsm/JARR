from tests.base import JarrFlaskCommon
from tests.utils import update_on_all_objs
from jarr.controllers import (ArticleController, CategoryController,
                              ClusterController, FeedController,
                              UserController)


class OnePageAppTest(JarrFlaskCommon):

    def setUp(self):
        super().setUp()
        self.user = UserController().get(id=2)

    def assertClusterCount(self, count, filters=None, expected_payload=None):
        filters = filters or {}
        resp = self.jarr_client('get', 'clusters',
                data=filters, user=self.user.login)
        self.assertStatusCode(200, resp)
        clusters = resp.json
        self.assertEqual(count, len(clusters))
        if expected_payload is not None:
            for cluster in clusters:
                differing_keys = [key for key in expected_payload
                                  if expected_payload[key] != cluster[key]]
                err_msg = "got differing values for:" + ','.join(
                        ["%s (%r!=%r)" % (key, expected_payload[key],
                                          cluster[key])
                         for key in differing_keys])
                self.assertEqual([], differing_keys, err_msg)
        return clusters

    def test_list_feeds(self):
        resp = self.jarr_client('get', 'list-feeds', user=self.user.login)
        fcount = FeedController(self.user.id).read().count()
        ccount = CategoryController(self.user.id).read().count()
        self.assertEqual(fcount + ccount + 1, len(resp.json))
        self.assertEqual(fcount,
                         len([r for r in resp.json if r['type'] == 'feed']))
        self.assertEqual(ccount,
                         len([r for r in resp.json if r['type'] == 'categ']))

    def test_unreads(self):
        resp = self.jarr_client('get', 'unreads', user=self.user.login)
        self.assertStatusCode(200, resp)
        result = resp.json
        self.assertEqual(10, len(result))
        self.assertEqual(12, sum([value for key, value in result.items()
                                  if "categ" in key]))
        self.assertEqual(18, sum([value for key, value in result.items()
                                  if "feed" in key]))

        self._mark_as_read(0, {'filter': 'unread'})

        resp = self.jarr_client('get', 'unreads', user=self.user.login)
        self.assertStatusCode(200, resp)
        result = resp.json
        self.assertEqual(0, len(result))

    def test_cluster_listing(self):
        clusters = self.assertClusterCount(18)
        self.assertClusterCount(18, {'filter': 'unread'})
        self.assertClusterCount(0, {'filter': 'liked'})
        self.jarr_client('put', 'cluster', clusters[0]['id'],
                         data={'liked': True}, user=self.user.login)
        self.assertClusterCount(1, {'filter': 'liked'})
        self.assertClusterCount(3, {'feed_id': 1}, {"feeds_id": [1]})
        self.assertClusterCount(3, {'feed_id': 2}, {"feeds_id": [2]})

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

    def test_middle_panel_filtered_on_feed(self):
        feed_id = self.user.feeds[0].id
        clusters = self.assertClusterCount(3, {'feed_id': feed_id})
        for cluster in clusters:
            self.assertIn(feed_id, cluster['feeds_id'])

    def _mark_as_read(self, expected_unread_count, filters=None):
        filters = filters or {}
        resp = self.jarr_client('put', 'mark-all-as-read', data=filters,
                                user=self.user.login)
        self.assertStatusCode(200, resp)
        unread_count = sum(v for k, v in resp.json.items() if 'feed' in k)
        self.assertEqual(expected_unread_count, unread_count,
                         "expected %d unread clusters, got %d"
                         % (expected_unread_count, unread_count))

    def test_MarkClustersAsRead_put(self):
        self.assertClusterCount(18, {'filter': 'unread'})
        self._mark_as_read(18, {'filter': 'liked'})
        self.assertClusterCount(18, {'filter': 'unread'})
        self._mark_as_read(0, {'filter': 'unread'})
        self.assertClusterCount(0, {'filter': 'unread'})

    def test_MarkClustersAsRead_put_only_singles(self):
        feed = FeedController(self.user.id).read()[0]
        update_on_all_objs(feeds=[feed],
                           cluster_same_feed=True, cluster_enabled=True)
        # creating a new article that will cluster
        ArticleController(self.user.id).create(entry_id='new entry_id',
                title='new title', content='new content',
                feed_id=feed.id, link=feed.articles[0].link)
        ClusterController(self.user.id).clusterize_pending_articles()
        self.assertClusterCount(18, {'filter': 'unread'})
        # one per feed
        self._mark_as_read(2, {'only_singles': True, 'filter': 'unread'})
        self.assertClusterCount(1, {'filter': 'unread'})

    def test_MarkClustersAsRead_put_one_feed(self):
        self.assertClusterCount(18, {'filter': 'unread'})
        self._mark_as_read(15, {'filter': 'unread', 'feed_id': 1})
        self.assertClusterCount(15, {'filter': 'unread'})

    def test_MarkClustersAsRead_put_one_category(self):
        self.assertClusterCount(18, {'filter': 'unread'})
        self._mark_as_read(15, {'filter': 'unread', 'category_id': 1})
        self.assertClusterCount(15, {'filter': 'unread'})

    def test_MarkClustersAsRead_put_null_category(self):
        self.assertClusterCount(18, {'filter': 'unread'})
        self._mark_as_read(12, {'filter': 'unread', 'category_id': 0})
        self.assertClusterCount(12, {'filter': 'unread'})
