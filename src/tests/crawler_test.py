from tests.base import JarrFlaskCommon

import logging
from datetime import datetime, timezone

import feedparser
from mock import Mock, patch

from bootstrap import conf
from crawler.http_crawler import CrawlerScheduler
from web.controllers import FeedController, UserController
from lib.const import UNIX_START

logger = logging.getLogger('web')


class CrawlerTest(JarrFlaskCommon):

    def setUp(self):
        super().setUp()
        atom_file_path = 'src/tests/fixtures/example.feed.atom'
        with open(atom_file_path) as fd:
            self.new_entries_cnt = len(feedparser.parse(fd.read())['entries'])
            self.new_entries_cnt *= FeedController().read().count()
        self.wait_params = {'wait_for': 1, 'max_wait': 10, 'checks': 1}
        UserController().update({'login': 'admin'}, {'is_api': True})
        self._is_secure_served \
                = patch('web.lib.article_cleaner.is_secure_served')
        self._p_req = patch('requests.Session.request')
        self._p_con = patch('crawler.http_crawler.construct_feed_from')
        self.is_secure_served = self._is_secure_served.start()
        self.jarr_req = self._p_req.start()
        self.jarr_con = self._p_con.start()

        self.is_secure_served.return_value = True
        self.resp_status_code = 200
        self.resp_headers = {}
        self.resp_raise = None

        def _api_req(method, url, **kwargs):
            if url.startswith('feed') and len(url) == 6:
                class Proxy:
                    status_code = self.resp_status_code
                    headers = self.resp_headers

                    @classmethod
                    def raise_for_status(cls):
                        if self.resp_raise is None:
                            return
                        raise self.resp_raise

                    @property
                    def content(self):
                        with open(atom_file_path) as f:
                            return f.read()

                    text = content
                return Proxy()

            url = url.split(conf.API_ROOT)[1].strip('/')
            kwargs.pop('allow_redirects', None)
            kwargs.pop('json', None)
            if 'auth' in kwargs:
                kwargs['user'] = kwargs['auth'][0]
                del kwargs['auth']
            response = self._api(method.lower(), url, **kwargs)
            response.raise_for_status = Mock()
            return response

        self.jarr_con.return_value = {}
        self.jarr_req.side_effect = _api_req

    def tearDown(self):
        super().tearDown()
        self._is_secure_served.stop()
        self._p_req.stop()
        self._p_con.stop()

    def _reset_feeds_freshness(self, **kwargs):
        if 'expires' not in kwargs:
            kwargs['expires'] = UNIX_START
        if 'last_retrieved' not in kwargs:
            kwargs['last_retrieved'] = UNIX_START
        if 'etag' not in kwargs:
            kwargs['etag'] = ''
        if 'last_modified' not in kwargs:
            kwargs['last_modified'] = ''
        FeedController().update({}, kwargs)

    def test_http_crawler_add_articles(self):
        scheduler = CrawlerScheduler('admin', 'admin')
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(36, len(resp.json()))

        scheduler.run()
        scheduler.wait(**self.wait_params)
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(36 + self.new_entries_cnt, len(resp.json()))

        for art in resp.json():
            self.assertFalse('srcset=' in art['content'])
            self.assertFalse('src="/' in art['content'])

        self.resp_status_code = 304
        scheduler.run()
        scheduler.wait(**self.wait_params)
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(36 + self.new_entries_cnt, len(resp.json()))

    def test_no_add_on_304(self):
        scheduler = CrawlerScheduler('admin', 'admin')
        self.resp_status_code = 304
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(36, len(resp.json()))

        scheduler.run()
        scheduler.wait(**self.wait_params)
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(36, len(resp.json()))

    @patch('crawler.http_crawler.JarrUpdater.callback')
    def test_no_add_feed_skip(self, jarr_updated_callback):
        scheduler = CrawlerScheduler('admin', 'admin')
        self.resp_status_code = 304
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(36, len(resp.json()))
        FeedController().update({}, {'filters': [{"type": "tag contains",
                                                  "action on": "match",
                                                  "pattern": "pattern5",
                                                  "action": "skipped"},
                                                 {"type": "simple match",
                                                  "action on": "match",
                                                  "pattern": "pattern5",
                                                  "action": "mark as read"},
                                                 {"type": "regex",
                                                  "action on": "match",
                                                  "pattern": "pattern5",
                                                  "action": "skipped"}]})

        scheduler.run()
        scheduler.wait(**self.wait_params)
        self.assertFalse(jarr_updated_callback.called,
                "all articles should have been skipped")
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(36, len(resp.json()))

    def test_matching_etag(self):
        self._reset_feeds_freshness(etag='fake etag')
        self.resp_headers = {'etag': 'fake etag'}
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(36, len(resp.json()))
        scheduler = CrawlerScheduler('admin', 'admin')

        scheduler.run()
        scheduler.wait(**self.wait_params)
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(36, len(resp.json()))

        self._reset_feeds_freshness(etag='jarr/fake etag')
        self.resp_headers = {'etag': 'jarr/fake etag'}

        scheduler.run()
        scheduler.wait(**self.wait_params)
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(36, len(resp.json()))

        self._reset_feeds_freshness(etag='jarr/fake etag')
        self.resp_headers = {'etag': '########################'}

        scheduler.run()
        scheduler.wait(**self.wait_params)
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(36 + self.new_entries_cnt, len(resp.json()))
