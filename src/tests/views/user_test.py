from io import BytesIO

from mock import patch

from tests.base import JarrFlaskCommon
from web.controllers import (ArticleController, CategoryController,
                             ClusterController, FeedController, UserController)


class BaseUiTest(JarrFlaskCommon):

    def setUp(self):
        super().setUp()
        login = 'user1'
        self.user = UserController().get(login=login)
        self.user2 = UserController().get(login='user2')
        self.app.post('/login', data={'login': login, 'password': login},
                      follow_redirects=True)
        self.fctrl = FeedController(self.user.id)
        self.cctrl = CategoryController(self.user.id)
        self.uctrl = UserController()

    def tearDown(self):
        self.app.get('/logout', follow_redirects=True)

    def test_opml_dump_and_restore(self):
        # downloading OPML export file
        resp = self.app.get('/user/opml/export')
        self.assertStatusCode(200, resp)
        opml_dump = resp.data.decode()
        self.assertTrue(
                opml_dump.startswith('<?xml version="1.0" encoding="utf-8"'))
        self.assertTrue(opml_dump.endswith('</opml>'))
        # cleaning db
        actrl = ArticleController(self.user.id)
        for item in actrl.read():
            actrl.delete(item.id)
        self.assertEqual(0, ClusterController(self.user.id).read().count())
        self.assertEqual(0, ArticleController(self.user.id).read().count())
        no_category_feed = []
        existing_feeds = {}
        for feed in self.fctrl.read():
            if feed.category:
                if feed.category.name in existing_feeds:
                    existing_feeds[feed.category.name].append(feed.title)
                else:
                    existing_feeds[feed.category.name] = [feed.title]
            else:
                no_category_feed.append(feed.title)

            self.fctrl.delete(feed.id)
        for category in self.cctrl.read():
            self.cctrl.delete(category.id)
        # re-importing OPML
        resp = self.app.post('/user/opml/import',
                data={'opml.xml': (BytesIO(resp.data), 'opml.xml')})
        self.assertStatusCode(302, resp)
        self._check_opml_imported(existing_feeds, no_category_feed)

        resp = self.app.post('/user/opml/import',
                data={'opml.xml': (BytesIO(resp.data), 'opml.xml')})
        self.assertStatusCode(302, resp)

    def _check_opml_imported(self, existing_feeds, no_category_feed):
        self.assertEqual(sum(map(len, existing_feeds.values()))
                          + len(no_category_feed), self.fctrl.read().count())
        self.assertEqual(len(existing_feeds), self.cctrl.read().count())
        for feed in self.fctrl.read():
            if feed.category:
                self.assertTrue(feed.category.name in existing_feeds,
                        "%s not in %r" % (feed.category.name,
                                          list(existing_feeds.keys())))
                self.assertTrue(
                        feed.title in existing_feeds[feed.category.name],
                        "%s not in %r" % (feed.title,
                                          existing_feeds[feed.category.name]))
            else:
                self.assertTrue(feed.title in no_category_feed)

    def test_user_delete(self):
        # test fail delete other user
        self.app.get('/user/delete_account/%d' % self.user2.id)
        self.assertEqual(self.user2.id, self.uctrl.get(login='user2').id)
        # test delete other user because admin
        self.uctrl.update({'id': self.user.id}, {'is_admin': True})
        self.app.get('/user/delete_account/%d' % self.user2.id)
        self.assertEqual(0, self.uctrl.read(login='user2').count())
        # test delete own user
        self.uctrl.update({'id': self.user.id}, {'is_admin': False})
        self.app.get('/user/delete_account/%d' % self.user.id)
        self.assertEqual(0, self.uctrl.read(id=self.user.id).count())

    def test_user_profile(self):
        login_form = '<input class="form-control" id="login" '\
                     'name="login" type="text" value="%s">'
        resp = self.app.get('/user/profile')
        self.assertStatusCode(200, resp)
        self.assertTrue((login_form % self.user.login) in resp.data.decode())
        resp = self.app.get('/user/profile/%d' % self.user.id)
        self.assertStatusCode(200, resp)
        self.assertTrue((login_form % self.user.login) in resp.data.decode())
        resp = self.app.get('/user/profile/%d' % self.user2.id)
        self.assertStatusCode(302, resp)
        self.uctrl.update({'id': self.user.id}, {'is_admin': True})
        resp = self.app.get('/user/profile/%d' % self.user2.id)
        self.assertStatusCode(200, resp)
        self.assertTrue((login_form % self.user2.login) in resp.data.decode())

    @patch('lib.emails.send')
    def test_password_recovery(self, mock_emails_send):
        self.app.get('/logout')
        self.assertEqual('', self.user.renew_password_token)
        resp = self.app.post('/user/gen_pass_token',
                             data={'email': self.user.email})
        self.assertStatusCode(200, resp)
        self.assertTrue(mock_emails_send.called)
        mail_content = mock_emails_send.call_args[1]['plaintext']

        self.assertTrue('/user/recover/' in mail_content)
        self.assertTrue('\n\nRegards,' in mail_content)
        token = mail_content.split('/user/recover/')[1].split('\n\nRegards')[0]
        self.assertEqual(token,
                self.uctrl.get(id=self.user.id).renew_password_token)

        # recovering with wrong token
        resp = self.app.get('/user/recover/garbage')
        self.assertEqual(
                b'Token is not valid, please regenerate one', resp.data, )

        # recovering with non matching passwords
        resp = self.app.post('/user/recover/%s' % token,
                             data={'password': 'not matching',
                                   'password_conf': 'new_password'})
        self.assertTrue("Passwords don't match" in resp.data.decode())

        # true recovery
        old_password = self.user.password
        resp = self.app.post('/user/recover/%s' % token,
                             data={'password': 'new_password',
                                   'password_conf': 'new_password'})
        self.assertStatusCode(302, resp)
        self.assertNotEqual(old_password,
                self.uctrl.get(id=self.user.id).password)
        self.assertEqual('',
                self.uctrl.get(id=self.user.id).renew_password_token)

        # we're logged after password change
        self.assertStatusCode(200, self.app.get('/'))
        self.app.get('/logout')

        # we can log in with the new password
        self.app.post('/login', data={'login': self.user.login,
                                      'password': 'new_password'},
                      follow_redirects=True)
        self.assertStatusCode(200, self.app.get('/'))

    def test_password_update(self):
        old_password = self.user.password
        self.app.post('/user/password_update/%d' % self.user.id,
                data={'password': 'new_pass', 'password_conf': 'no matching'})
        user = self.uctrl.get(id=self.user.id)
        self.assertEqual(user.password, old_password)
        self.app.post('/user/password_update/%d' % self.user.id,
                data={'password': 'new_pass', 'password_conf': 'new_pass'})
        user = self.uctrl.get(id=self.user.id)
        self.assertNotEqual(user.password, old_password)

    def test_profile_update(self):
        data = {'email': 'not an email', 'is_admin': True}
        self.app.post('/user/profile_update/%d' % self.user2.id, data=data)
        user2 = self.uctrl.get(id=self.user2.id)
        self.assertFalse(user2.is_admin)
        self.assertNotEqual(user2.email, 'not an email')

        self.uctrl.update({'id': self.user.id}, {'is_admin': True})
        data['email'], data['login'] = 'a.valid@email.fake', self.user2.login
        self.app.post('/user/profile_update/%d' % self.user2.id, data=data)
        user2 = self.uctrl.get(id=self.user2.id)
        self.assertTrue(user2.is_admin)
        self.assertEqual(user2.email, data['email'])
