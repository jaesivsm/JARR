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
                len(json.loads(resp.data.decode('utf8'))['articles']))
        resp = self.app.get('/middle_panel?filter=unread')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(9,
                len(json.loads(resp.data.decode('utf8'))['articles']))
        resp = self.app.get('/middle_panel?query=test')
        self.assertEquals(200, resp.status_code)
        resp = self.app.get('/middle_panel?query=test&search_title=true')
        self.assertEquals(200, resp.status_code)
        resp = self.app.get('/middle_panel?query=test&search_content=true')
        self.assertEquals(200, resp.status_code)
        resp = self.app.get('/middle_panel?query=test'
                            '&search_title=true&search_content=true')
        self.assertEquals(200, resp.status_code)
        resp = self.app.get('/middle_panel?filed_type=feed&filter_id=1')
        self.assertEquals(200, resp.status_code)
        resp = self.app.get('/middle_panel?filter_type=category&filter_id=0')
        self.assertEquals(200, resp.status_code)

        # marking all as read
        resp = self.app.put('/mark_all_as_read', data='{}',
                headers={'Content-Type': 'application/json'})
        self.assertEquals(200, resp.status_code)
        resp = self.app.get('/middle_panel?filter=unread')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(0,
                len(json.loads(resp.data.decode('utf8'))['articles']))

    def test_getart(self):
        resp = self.app.get('/getart/1',
                headers={'Content-Type': 'application/json'})
        self.assertEquals(200, resp.status_code)
        self.app.get('/logout')
        self.app.post('/login', data={'login': 'user2', 'password': 'user2'})
        resp = self.app.get('/getart/1',
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
