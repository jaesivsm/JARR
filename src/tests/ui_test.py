import json
from tests.base import JarrFlaskCommon


class BaseUiTest(JarrFlaskCommon):

    def setUp(self):
        super().setUp()
        self.app.post('/login', data={'login': 'user1', 'password': 'user1'})

    def tearDown(self):
        self.app.get('/logout')

    def assertClusterCount(self, count, filters=''):
        if filters and not filters.startswith('?'):
            filters = '?' + filters
        resp = self.app.get('/middle_panel%s' % filters)
        self.assertEquals(200, resp.status_code)
        clusters = json.loads(resp.data.decode('utf8'))['clusters']
        self.assertEquals(count, len(clusters))
        return clusters

    def test_menu(self):
        resp = self.app.get('/menu')
        self.assertEquals(200, resp.status_code)

    def test_middle_panel(self):
        clusters = self.assertClusterCount(9)
        self.assertClusterCount(9, 'filter=unread')
        self.assertClusterCount(0, 'filter=liked')
        self._api('put', 'cluster', clusters[0]['id'],
                  data={'liked': True}, user='user1')
        self.assertClusterCount(1, 'filter=liked')
        self.assertClusterCount(3, 'filter_type=feed_id&filter_id=1')
        self.assertClusterCount(3, 'filter_type=feed_id&filter_id=1')
        self.assertClusterCount(3, 'filter_type=category_id&filter_id=0')

    def test_search(self):
        self.assertClusterCount(0, 'query=test')
        self.assertClusterCount(9, 'query=user1')
        self.assertClusterCount(3, 'query=feed1&search_title=true')
        self.assertClusterCount(3, 'query=user1%20feed0&search_content=true')
        self.assertClusterCount(1,
                'query=content 3&search_title=true&search_content=true')

    def test_middle_panel_filtered_on_category(self):
        cat_id = 1
        clusters = self.assertClusterCount(3,
                'filter_type=category_id&filter_id=%d' % cat_id)
        for cluster in clusters:
            self.assertTrue(cat_id in cluster['categories_id'],
                    "%d not in %r" % (cat_id, cluster['categories_id']))

    def test_middle_panel_filtered_on_feed(self):
        feed_id = 3
        clusters = self.assertClusterCount(3,
                'filter_type=feed_id&filter_id=%d' % feed_id)
        for cluster in clusters:
            self.assertTrue(feed_id in cluster['feeds_id'],
                    "%d not in %r" % (feed_id, cluster['feeds_id']))

    def _mark_as_read(self, filters={}):
        resp = self.app.put('/mark_all_as_read', data=json.dumps(filters),
                headers={'Content-Type': 'application/json'})
        self.assertEquals(200, resp.status_code)

    def test_mark_all_as_read(self):
        self.assertClusterCount(9, 'filter=unread')
        self._mark_as_read()
        self.assertClusterCount(0, 'filter=unread')

    def test_mark_all_as_read_filter(self):
        self.assertClusterCount(9, 'filter=unread')
        self._mark_as_read({'filter': "unread",
                            'filter_type': None, 'filter_id': None})
        self.assertClusterCount(0, 'filter=unread')

    def test_mark_feed_as_read(self):
        self.assertClusterCount(9, 'filter=unread')
        self._mark_as_read({"filter": "unread",
                            "filter_type": "feed_id", "filter_id": 1})
        self.assertClusterCount(6, 'filter=unread')

    def test_mark_category_as_read(self):
        self.assertClusterCount(9, 'filter=unread')
        self._mark_as_read({"filter": "unread", "filter_type": "category_id",
                            "filter_id": 1})
        self.assertClusterCount(6, 'filter=unread')

    def test_mark_no_category_as_read(self):
        self.assertClusterCount(9, 'filter=unread')
        self._mark_as_read({"filter": "unread", "filter_type": "category_id",
                            "filter_id": 0})
        self.assertClusterCount(6, 'filter=unread')

    def test_getclu(self):
        resp = self.app.get('/getclu/1',
                headers={'Content-Type': 'application/json'})
        self.assertEquals(200, resp.status_code)
        self.app.get('/logout')
        self.app.post('/login', data={'login': 'user2', 'password': 'user2'})
        resp = self.app.get('/getclu/1',
                headers={'Content-Type': 'application/json'})
        self.assertEquals(404, resp.status_code)

    def test_login_logout(self):
        self.assertEquals(302, self.app.get('/logout').status_code)
        self.assertEquals(302, self.app.get('/').status_code)
        self.assertEquals(200, self.app.get('/login').status_code)
        resp = self.app.post('/login',
                data={'login': 'admin', 'password': 'admin'})
        self.assertEquals(302, resp.status_code)
        self.assertEquals(200, self.app.get('/').status_code)
        self.assertEquals(302, self.app.get('/logout').status_code)
        self.assertEquals(302, self.app.get('/').status_code)
