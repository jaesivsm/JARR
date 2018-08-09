import logging
import unittest

import feedparser
from mock import Mock, patch
from the_conf import TheConf

from tests.base import JarrFlaskCommon

from jarr.bootstrap import conf
from jarr.controllers import FeedController, UserController
from jarr_crawler.http_crawler import (main as crawler, response_etag_match,
                                       response_calculated_etag_match,
                                       set_feed_error, clean_feed)
from jarr_common.utils import to_hash
from jarr_common.const import UNIX_START

logger = logging.getLogger('jarr')
BASE_COUNT = 36


def get_first_call(query_jarr):
    method, urn, _, _, data = query_jarr.mock_calls[0][1]
    return method, urn, data


class CrawlerTest(JarrFlaskCommon):

    def setUp(self):
        super().setUp()
        with open('tests/fixtures/example.feed.atom') as fd:
            self._content = fd.read()
        self.new_entries_cnt = len(feedparser.parse(self._content)['entries'])
        self.new_entries_cnt *= FeedController().read().count()
        self.wait_params = {'wait_for': 1, 'max_wait': 10, 'checks': 1}
        UserController().update({'login': 'admin'}, {'is_api': True})
        self._is_secure_served \
                = patch('jarr.lib.article_cleaner.is_secure_served')
        self._p_req = patch('jarr_crawler.http_crawler.requests.api.request')
        self._p_con = patch('jarr_crawler.http_crawler.construct_feed_from')
        self.is_secure_served = self._is_secure_served.start()
        self.jarr_req = self._p_req.start()
        self.jarr_con = self._p_con.start()

        self.is_secure_served.return_value = True
        self.resp_status_code = 200
        self.resp_headers = {}
        self.resp_raise = None

        def _api_req(method, url, **kwargs):
            if url.startswith('feed') and len(url) == 6:
                resp = Mock(status_code=self.resp_status_code,
                            headers=self.resp_headers, history=[],
                            content=self._content, text=self._content)
                resp.raise_for_status.return_value = self.resp_raise
                return resp

            url = url.split(conf.api_root)[1].strip('/')
            kwargs.pop('allow_redirects', None)
            kwargs.pop('params', None)
            kwargs.pop('json', None)
            if 'auth' in kwargs:
                kwargs['user'] = kwargs['auth'][0]
                del kwargs['auth']
            response = self._api(method.lower(), url, **kwargs)
            response.raise_for_status = Mock()
            return response

        self.jarr_con.return_value = {}
        self.jarr_req.side_effect = _api_req
        conf.crawler.login = 'admin'
        conf.crawler.passwd = 'admin'

    def tearDown(self):
        self._is_secure_served.stop()
        self._p_req.stop()
        self._p_con.stop()
        super().tearDown()

    @staticmethod
    def _reset_feeds_freshness(**kwargs):
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
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEqual(BASE_COUNT, len(resp.json()))

        crawler(conf)
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEqual(BASE_COUNT + self.new_entries_cnt, len(resp.json()))

        for art in resp.json():
            self.assertFalse('srcset=' in art['content'])
            self.assertFalse('src="/' in art['content'])

        self.resp_status_code = 304
        crawler(conf)
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEqual(BASE_COUNT + self.new_entries_cnt, len(resp.json()))

    def test_no_add_on_304(self):
        self.resp_status_code = 304
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEqual(BASE_COUNT, len(resp.json()))

        crawler(conf)
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEqual(BASE_COUNT, len(resp.json()))

    def test_no_add_feed_skip(self):
        self.resp_status_code = 304
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEqual(BASE_COUNT, len(resp.json()))
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

        crawler(conf)
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEqual(BASE_COUNT, len(resp.json()))

    def test_matching_etag(self):
        self._reset_feeds_freshness(etag='fake etag')
        self.resp_headers = {'etag': 'fake etag'}
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEqual(BASE_COUNT, len(resp.json()))

        crawler(conf)
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEqual(BASE_COUNT, len(resp.json()))

        self._reset_feeds_freshness(etag='jarr/"%s"' % to_hash(self._content))
        self.resp_headers = {'etag': 'jarr/"%s"' % to_hash(self._content)}

        crawler(conf)
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEqual(BASE_COUNT, len(resp.json()))

        self._reset_feeds_freshness(etag='jarr/fake etag')
        self.resp_headers = {'etag': '########################'}

        crawler(conf)
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEqual(BASE_COUNT + self.new_entries_cnt, len(resp.json()))


class CrawlerMethodsTest(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.feed = {'user_id': 1, 'id': 1, 'title': 'title',
                     'description': 'description',
                     'etag': '', 'error_count': 5, 'link': 'link'}
        self.resp = Mock(text='text', headers={}, status_code=304, history=[])
        self.pool = []

    def tearDown(self):
        TheConf._TheConf__instance = None

    def test_etag_matching_w_constructed_etag(self):
        self.feed['etag'] = 'jarr/"%s"' % to_hash('text')
        self.assertFalse(response_etag_match(self.feed, self.resp))
        self.assertTrue(response_calculated_etag_match(self.feed, self.resp))

    def test_etag_no_matching_wo_etag(self):
        self.assertFalse(response_etag_match(self.feed, self.resp))
        self.assertFalse(response_calculated_etag_match(self.feed, self.resp))

    def test_etag_matching(self):
        self.resp.headers['etag'] = self.feed['etag'] = 'etag'
        self.assertTrue(response_etag_match(self.feed, self.resp))
        self.assertFalse(response_calculated_etag_match(self.feed, self.resp))

    @patch('jarr_crawler.http_crawler.query_jarr')
    def test_set_feed_error_w_error(self, query_jarr):
        original_error_count = self.feed['error_count']
        set_feed_error(self.feed, conf, self.pool, Exception('an error'))
        method, urn, data = get_first_call(query_jarr)

        self.assertEqual('put', method)
        self.assertEqual('feed/%d' % self.feed['id'], urn)
        self.assertEqual(original_error_count + 1, data['error_count'])
        self.assertEqual('an error', data['last_error'])

    @patch('jarr_crawler.http_crawler.query_jarr')
    def test_set_feed_error_w_parsed(self, query_jarr):
        original_error_count = self.feed['error_count']
        set_feed_error(self.feed, conf, self.pool,
                       parsed_feed={'bozo_exception': 'an error'})
        method, urn, data = get_first_call(query_jarr)
        self.assertEqual('put', method)
        self.assertEqual('feed/%d' % self.feed['id'], urn)
        self.assertEqual(original_error_count + 1, data['error_count'])
        self.assertEqual('an error', data['last_error'])

    @patch('jarr_crawler.http_crawler.query_jarr')
    def test_clean_feed(self, query_jarr):
        clean_feed(self.feed, conf, self.pool, self.resp)
        method, urn, data = get_first_call(query_jarr)

        self.assertEqual('put', method)
        self.assertEqual('feed/%d' % self.feed['id'], urn)
        self.assertTrue('link' not in data)
        self.assertTrue('title' not in data)
        self.assertTrue('description' not in data)
        self.assertTrue('site_link' not in data)
        self.assertTrue('icon_url' not in data)

    @patch('jarr_crawler.http_crawler.query_jarr')
    def test_clean_feed_update_link(self, query_jarr):
        self.resp.history.append(Mock(status_code=301))
        self.resp.url = 'new_link'
        clean_feed(self.feed, conf, self.pool, self.resp)
        method, urn, data = get_first_call(query_jarr)

        self.assertEqual('put', method)
        self.assertEqual('feed/%d' % self.feed['id'], urn)
        self.assertEqual('new_link', data['link'])
        self.assertTrue('title' not in data)
        self.assertTrue('description' not in data)
        self.assertTrue('site_link' not in data)
        self.assertTrue('icon_url' not in data)

    @patch('jarr_crawler.http_crawler.construct_feed_from')
    @patch('jarr_crawler.http_crawler.query_jarr')
    def test_clean_feed_w_constructed(self, query_jarr, construct_feed_mock):
        construct_feed_mock.return_value = {'description': 'new description'}
        clean_feed(self.feed, conf, self.pool, self.resp, True)
        method, urn, data = get_first_call(query_jarr)

        self.assertEqual('put', method)
        self.assertEqual('feed/%d' % self.feed['id'], urn)
        self.assertEqual('new description', data['description'])
        self.assertTrue('link' not in data)
        self.assertTrue('title' not in data)
        self.assertTrue('site_link' not in data)
        self.assertTrue('icon_url' not in data)
