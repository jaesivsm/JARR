from io import BytesIO

from tests.base import JarrFlaskCommon
from jarr.controllers import (ArticleController, CategoryController,
        ClusterController, FeedController, UserController)


class OPMLTest(JarrFlaskCommon):

    def setUp(self):
        super().setUp()
        login = 'user1'
        self.user = UserController().get(login=login)
        self.user2 = UserController().get(login='user2')
        self.fctrl = FeedController(self.user.id)
        self.cctrl = CategoryController(self.user.id)
        self.uctrl = UserController()

    def test_opml_dump_and_restore(self):
        # downloading OPML export file
        resp = self.jarr_client('get', '/opml', user=self.user.login)
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
        import_resp = self.jarr_client('post', 'opml', to_json=False,
                data={'opml_file': (BytesIO(resp.data), 'opml.xml')},
                headers=None,
                user=self.user.login)
        self.assertStatusCode(201, import_resp)
        self.assertEqual(0, import_resp.json['existing'])
        self.assertEqual(0, import_resp.json['failed'])
        self._check_opml_imported(existing_feeds, no_category_feed)

        import_resp = self.jarr_client('post', 'opml', to_json=False,
                data={'opml_file': (BytesIO(resp.data), 'opml.xml')},
                headers=None,
                user=self.user.login)
        self.assertStatusCode(200, import_resp)
        self.assertEqual(0, import_resp.json['created'])
        self.assertEqual(0, import_resp.json['failed'])

    def _check_opml_imported(self, existing_feeds, no_category_feed):
        self.assertEqual(sum(map(len, existing_feeds.values()))
                          + len(no_category_feed), self.fctrl.read().count())
        self.assertEqual(len(existing_feeds), self.cctrl.read().count())
        for feed in self.fctrl.read():
            if feed.category:
                self.assertIn(feed.category.name, existing_feeds)
                self.assertIn(feed.title, existing_feeds[feed.category.name])
            else:
                self.assertIn(feed.title, no_category_feed)
