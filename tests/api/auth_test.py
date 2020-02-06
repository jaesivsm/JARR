import urllib
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
        email = urllib.parse.quote_plus(self.user.email)
        resp = self.jarr_client('post', 'auth_recovery', email)
        self.assertStatusCode(204, resp)
        self.assertTrue(mock_emails_send.called)
        mail_content = mock_emails_send.call_args[1]['plaintext']

        self.assertIn('auth_recovery?', mail_content)
        self.assertIn('\n\nRegards,', mail_content)
        qs = mail_content.split('auth_recovery?')[1].split('\n\n')[0]
        token = urllib.parse.parse_qs(qs)['token'][0]
        self.assertEqual(token,
                self.uctrl.get(id=self.user.id).renew_password_token)

        # recovering with wrong token
        data = {'password': 'new_password',
                'email': 'fake@email', 'token': 'token'}
        resp = self.jarr_client('put', 'auth_recovery', data=data)
        self.assertStatusCode(404, resp)
        data['email'] = self.user.email
        resp = self.jarr_client('put', 'auth_recovery', data=data)
        self.assertStatusCode(403, resp)
        data['email'], data['token'] = 'fake@email', token
        resp = self.jarr_client('put', 'auth_recovery', data=data)
        self.assertStatusCode(404, resp)

        # true recovery
        old_password = self.user.password
        data['email'], data['token'] = self.user.email, token
        resp = self.jarr_client('put', 'auth_recovery', data=data)
        self.assertStatusCode(204, resp)
        self.assertNotEqual(old_password,
                self.uctrl.get(id=self.user.id).password)
        self.assertEqual('',
                self.uctrl.get(id=self.user.id).renew_password_token)
