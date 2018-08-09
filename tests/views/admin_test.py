from tests.base import JarrFlaskCommon
from jarr.controllers import UserController


class BaseUiTest(JarrFlaskCommon):

    def setUp(self):
        super().setUp()
        self.uctrl = UserController()
        self.admin = self.uctrl.get(login='admin')
        self.user = self.uctrl.get(login='user1')
        self.user2 = self.uctrl.get(login='user2')

    def login(self, user):
        return self.app.post('/login', follow_redirects=True,
                data={'login': user.login, 'password': user.login})

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_dashboard_forbidden(self):
        self.assertFalse(self.user.is_admin)
        self.login(self.user)
        resp = self.app.get('/admin/dashboard')
        self.assertStatusCode(302, resp)
        self.logout()

    def test_dashboard(self):
        self.login(self.admin)
        resp = self.app.get('/admin/dashboard')
        self.assertStatusCode(200, resp)
        self.logout()

    def test_user_page_forbidden(self):
        self.assertFalse(self.user.is_admin)
        self.login(self.user)
        resp = self.app.get('/admin/user/%d' % self.user2.id)
        self.assertStatusCode(302, resp)
        self.logout()

    def test_user_page_not_found(self):
        self.login(self.admin)
        resp = self.app.get('/admin/user/-1')
        self.assertStatusCode(404, resp)
        self.logout()

    def test_user_page(self):
        self.login(self.admin)
        resp = self.app.get('/admin/user/%d' % self.user.id)
        self.assertStatusCode(200, resp)
        self.logout()

    def test_toggle_user_forbidden(self):
        self.assertTrue(self.uctrl.get(id=self.user.id).is_active)
        self.assertTrue(self.uctrl.get(id=self.user2.id).is_active)
        self.assertFalse(self.user.is_admin)
        self.login(self.user)
        self.assertStatusCode(403,
                self.app.get('/admin/toggle_user/%d' % self.user2.id))
        self.logout()
        self.assertTrue(self.uctrl.get(id=self.user.id).is_active)
        self.assertTrue(self.uctrl.get(id=self.user2.id).is_active)

    def test_toggle_user_not_found(self):
        self.assertTrue(self.uctrl.get(id=self.user.id).is_active)
        self.assertTrue(self.uctrl.get(id=self.user2.id).is_active)
        self.login(self.admin)
        resp = self.app.get('/admin/toggle_user/-1')
        self.assertStatusCode(404, resp)
        self.logout()
        self.assertTrue(self.uctrl.get(id=self.user.id).is_active)
        self.assertTrue(self.uctrl.get(id=self.user2.id).is_active)

    def test_toggle_user(self):
        self.assertTrue(self.uctrl.get(id=self.user.id).is_active)
        self.login(self.admin)
        resp = self.app.get('/admin/toggle_user/%d' % self.user.id)
        self.assertStatusCode(302, resp)
        self.assertFalse(self.uctrl.get(id=self.user.id).is_active)
        self.logout()
