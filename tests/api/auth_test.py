from mock import patch

from tests.base import JarrFlaskCommon
from jarr.controllers import UserController


class AuthTest(JarrFlaskCommon):

    def setUp(self):
        super().setUp()
        login = 'user1'
        self.user = UserController().get(login=login)
        self.user2 = UserController().get(login='user2')
        self.uctrl = UserController()

    @patch('jarr.lib.emails.send')
    def test_password_recovery(self, mock_emails_send):
        self.assertEqual('', self.user.renew_password_token)
        resp = self.jarr_client('post', '/auth/recovery',
                data={'login': self.user.login, 'email': self.user.email})
        self.assertStatusCode(204, resp)
        self.assertTrue(mock_emails_send.called)
        mail_content = mock_emails_send.call_args[1]['plaintext']

        self.assertIn('/auth/recovery/%s/%s/' % (self.user.login,
                                                 self.user.email),
                      mail_content)
        self.assertIn('\n\nRegards,', mail_content)
        token = mail_content.split('/')[-1].split('\n\n')[0]
        self.assertEqual(token,
                self.uctrl.get(id=self.user.id).renew_password_token)

        # recovering with wrong token
        data = {'password': 'new_password', "login": self.user.login,
                'email': 'fake@email', 'token': 'token'}
        resp = self.jarr_client('put', '/auth/recovery', data=data)
        self.assertStatusCode(404, resp)
        data['email'] = self.user.email
        resp = self.jarr_client('put', '/auth/recovery', data=data)
        self.assertStatusCode(403, resp)
        data['email'], data['token'] = 'fake@email', token
        resp = self.jarr_client('put', '/auth/recovery', data=data)
        self.assertStatusCode(404, resp)

        # true recovery
        old_password = self.user.password
        data['email'], data['token'] = self.user.email, token
        resp = self.jarr_client('put', '/auth/recovery', data=data)
        self.assertStatusCode(204, resp)
        self.assertNotEqual(old_password,
                self.uctrl.get(id=self.user.id).password)
        self.assertEqual('',
                self.uctrl.get(id=self.user.id).renew_password_token)
