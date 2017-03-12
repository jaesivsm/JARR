from tests.base import BaseJarrTest, JarrFlaskCommon

import logging
import unittest
from datetime import datetime, timezone

import feedparser
from mock import Mock, patch

from bootstrap import conf
from crawler.http_crawler import CrawlerScheduler, FeedCrawler
from web.controllers import FeedController, UserController
from lib.utils import to_hash
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
                with open(atom_file_path) as f:
                    content = f.read()
                    resp = Mock(status_code=self.resp_status_code,
                                headers=self.resp_headers,
                                content=content, text=content, history=[])
                resp.raise_for_status.return_value = self.resp_raise
                return resp

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


class CrawlerMethodsTest(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.feed = {'user_id': 1, 'id': 1, 'title': 'title',
                     'description': 'description',
                     'etag': '', 'error_count': 5, 'link': 'link'}
        self.resp = Mock(text='text', headers={}, status_code=304, history=[])
        self.crawler = FeedCrawler(self.feed, Mock())

    def test_etag_matching_w_constructed_etag(self):
        self.feed['etag'] = 'jarr/"%s"' % to_hash('text')
        self.assertTrue(self.crawler.response_match_cache(self.resp))

    def test_etag_no_matching_wo_etag(self):
        self.assertFalse(self.crawler.response_match_cache(self.resp))

    def test_etag_matching(self):
        self.resp.headers['etag'] = self.feed['etag'] = 'etag'
        self.assertTrue(self.crawler.response_match_cache(self.resp))

    def test_set_feed_error_w_error(self):
        original_error_count = self.feed['error_count']
        self.crawler.query_jarr = Mock()
        self.crawler.set_feed_error(Exception('an error'))
        call = self.crawler.query_jarr.mock_calls[0][1]

        self.assertEquals('put', call[0])
        self.assertEquals('feed/%d' % self.feed['id'], call[1])
        self.assertEquals(original_error_count + 1, call[2]['error_count'])
        self.assertEquals('an error', call[2]['last_error'])

    def test_set_feed_error_w_parsed(self):
        original_error_count = self.feed['error_count']
        self.crawler.query_jarr = Mock()
        self.crawler.set_feed_error(parsed_feed={'bozo_exception': 'an error'})
        call = self.crawler.query_jarr.mock_calls[0][1]
        self.assertEquals('put', call[0])
        self.assertEquals('feed/%d' % self.feed['id'], call[1])
        self.assertEquals(original_error_count + 1, call[2]['error_count'])
        self.assertEquals('an error', call[2]['last_error'])

    def test_clean_feed(self):
        self.crawler.query_jarr = Mock()
        self.crawler.clean_feed(self.resp)
        call = self.crawler.query_jarr.mock_calls[0][1]

        self.assertEquals('put', call[0])
        self.assertEquals('feed/%d' % self.feed['id'], call[1])
        self.assertTrue('link' not in call[2])
        self.assertTrue('title' not in call[2])
        self.assertTrue('description' not in call[2])
        self.assertTrue('site_link' not in call[2])
        self.assertTrue('icon_url' not in call[2])

    def test_clean_feed_update_link(self):
        self.crawler.query_jarr = Mock()
        self.resp.history.append(Mock(status_code=301))
        self.resp.url = 'new_link'
        self.crawler.clean_feed(self.resp)
        call = self.crawler.query_jarr.mock_calls[0][1]

        self.assertEquals('put', call[0])
        self.assertEquals('feed/%d' % self.feed['id'], call[1])
        self.assertEquals('new_link', call[2]['link'])
        self.assertTrue('title' not in call[2])
        self.assertTrue('description' not in call[2])
        self.assertTrue('site_link' not in call[2])
        self.assertTrue('icon_url' not in call[2])

    @patch('crawler.http_crawler.construct_feed_from')
    def test_clean_feed_w_constructed(self, construct_feed_mock):
        construct_feed_mock.return_value = {'description': 'new description'}
        self.crawler.query_jarr = Mock()
        self.crawler.clean_feed(self.resp, True)
        call = self.crawler.query_jarr.mock_calls[0][1]

        self.assertEquals('put', call[0])
        self.assertEquals('feed/%d' % self.feed['id'], call[1])
        self.assertEquals('new description', call[2]['description'])
        self.assertTrue('link' not in call[2])
        self.assertTrue('title' not in call[2])
        self.assertTrue('site_link' not in call[2])
        self.assertTrue('icon_url' not in call[2])
