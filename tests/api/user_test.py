from tests.base import JarrFlaskCommon
from jarr.controllers import UserController


class UserTest(JarrFlaskCommon):

    def setUp(self):
        super().setUp()
        login = 'user1'
        self.user = UserController().get(login=login)
        self.user2 = UserController().get(login='user2')
        self.uctrl = UserController()

    def test_UserResource_get(self):
        resp = self.jarr_client('get', 'user', headers=None)
        self.assertStatusCode(401, resp)
        resp = self.jarr_client('get', 'user', user=self.user.login)
        self.assertStatusCode(200, resp)
        self.assertEqual(resp.json['login'], self.user.login)
        self.assertFalse('password' in resp.json)
        resp = self.jarr_client('get', 'user', user=self.user2.login)
        self.assertStatusCode(200, resp)
        self.assertEqual(resp.json['login'], self.user2.login)
        self.assertFalse('password' in resp.json)

    def test_UserResource_put(self):
        headers = {'Authorization': self.get_token_for(self.user2.login),
                   'Content-Type': 'application/json'}
        old_password = self.user2.password

        data = {'email': 'not an email', 'cluster_wake_up': True}
        resp = self.jarr_client('put', 'user', data=data, headers=headers)
        self.assertStatusCode(200, resp)
        user2 = self.uctrl.get(id=self.user2.id)
        self.assertEqual(user2.email, 'not an email')
        self.assertTrue(user2.cluster_wake_up)
        self.assertEqual(old_password, user2.password)

        data = {'password': 'new password'}
        resp = self.jarr_client('put', 'user', data=data, headers=headers)
        self.assertStatusCode(200, resp)
        updated_user = self.uctrl.get(id=self.user2.id)
        self.assertNotEqual(data['password'], updated_user.password)
        self.assertNotEqual(old_password, updated_user.password)
        self.assertTrue(updated_user.cluster_wake_up)

        data = {'login': self.user.login}
        resp = self.jarr_client('put', 'user', data=data, headers=headers)
        self.assertStatusCode(400, resp)

    def test_UserResource_delete(self):
        headers = {'Authorization': self.get_token_for(self.user2.login)}
        resp = self.jarr_client('delete', 'user', headers=headers)
        self.assertStatusCode(204, resp)
        resp = self.jarr_client('get', 'user', headers=headers)
        self.assertStatusCode(404, resp)
        self.assertIsNone(self.uctrl.read(id=self.user2.id).first())
