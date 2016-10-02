import json
from tests.base import JarrFlaskCommon


class BaseUiTest(JarrFlaskCommon):

    def setUp(self):
        super().setUp()
        self.app.post('/login', data={'login': 'user1', 'password': 'user1'})

    def tearDown(self):
        self.app.get('/logout')

    def test_menu(self):
        resp = self.app.get('/menu')
        self.assertEquals(200, resp.status_code)

    def test_middle_panel(self):
        resp = self.app.get('/middle_panel')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(9,
                len(json.loads(resp.data.decode('utf8'))['clusters']))
        resp = self.app.get('/middle_panel?filter=unread')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(9,
                len(json.loads(resp.data.decode('utf8'))['clusters']))

    def test_search(self):
        resp = self.app.get('/middle_panel?query=test')
        self.assertEquals(200, resp.status_code)
        resp = self.app.get('/middle_panel?query=test&search_title=true')
        self.assertEquals(200, resp.status_code)
        resp = self.app.get('/middle_panel?query=test&search_content=true')
        self.assertEquals(200, resp.status_code)
        resp = self.app.get('/middle_panel?query=test'
                            '&search_title=true&search_content=true')
        self.assertEquals(200, resp.status_code)

    def test_middle_panel_filtered_on_category(self):
        cat_id = 1
        resp = self.app.get(
                '/middle_panel?filter_type=category_id&filter_id=%d' % cat_id)
        self.assertEquals(200, resp.status_code)
        clusters = json.loads(resp.data.decode('utf8'))['clusters']
        for cluster in clusters:
            self.assertTrue(cat_id in cluster['categories_id'],
                    "%d not in %r" % (cat_id, cluster['categories_id']))
        self.assertEquals(3, len(clusters))

    def test_middle_panel_filtered_on_feed(self):
        feed_id = 3
        resp = self.app.get(
                '/middle_panel?filter_type=feed_id&filter_id=%d' % feed_id)
        clusters = json.loads(resp.data.decode('utf8'))['clusters']
        for cluster in clusters:
            self.assertTrue(feed_id in cluster['feeds_id'],
                    "%d not in %r" % (feed_id, cluster['feeds_id']))
        self.assertEquals(3, len(clusters))
        self.assertEquals(200, resp.status_code)        # marking all as read

    def test_mark_all_as_read(self):
        resp = self.app.put('/mark_all_as_read', data='{}',
                headers={'Content-Type': 'application/json'})
        self.assertEquals(200, resp.status_code)
        resp = self.app.get('/middle_panel?filter=unread')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(0,
                len(json.loads(resp.data.decode('utf8'))['clusters']))

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
