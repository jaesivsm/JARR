from tests.base import JarrFlaskCommon
import logging
from mock import Mock, patch
from datetime import datetime

import conf
from crawler.http_crawler import CrawlerScheduler
from web.controllers import UserController, FeedController
logger = logging.getLogger('web')


class CrawlerTest(JarrFlaskCommon):

    def setUp(self):
        super().setUp()
        UserController().update({'login': 'admin'}, {'is_api': True})
        self._p_req = patch('requests.Session.request')
        self._p_con = patch('crawler.http_crawler.construct_feed_from')
        self.jarr_req = self._p_req.start()
        self.jarr_con = self._p_con.start()

        self.resp_status_code = 200
        self.resp_headers = {}
        self.resp_raise = None

        def _api_req(method, url, **kwargs):
            if url in set('feed%d' % i for i in range(5)):
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
                        with open('src/tests/fixtures/example.feed.atom') as f:
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
        self._p_req.stop()
        self._p_con.stop()

    def _reset_feeds_freshness(self, **kwargs):
        if 'last_retrieved' not in kwargs:
            kwargs['last_retrieved'] = datetime(1970, 1, 1)
        if 'etag' not in kwargs:
            kwargs['etag'] = ''
        if 'last_modified' not in kwargs:
            kwargs['last_modified'] = ''
        FeedController().update({}, kwargs)

    def test_http_crawler_add_articles(self):
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(18, len(resp.json()))
        scheduler = CrawlerScheduler('admin', 'admin')
        scheduler.run()
        scheduler.wait()

        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(143, len(resp.json()))
        self.resp_status_code = 304
        scheduler.run()
        scheduler.wait()

        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(143, len(resp.json()))

    def test_no_add_on_304(self):
        self.resp_status_code = 304
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(18, len(resp.json()))
        scheduler = CrawlerScheduler('admin', 'admin')
        scheduler.run()
        scheduler.wait()

        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(18, len(resp.json()))

    def test_matching_etag(self):
        self._reset_feeds_freshness(etag='fake etag')
        self.resp_headers = {'etag': 'fake etag'}
        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(18, len(resp.json()))
        scheduler = CrawlerScheduler('admin', 'admin')
        scheduler.run()
        scheduler.wait()

        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(18, len(resp.json()))

        self._reset_feeds_freshness(etag='jarr/fake etag')
        self.resp_headers = {'etag': 'jarr/fake etag'}

        scheduler.run()
        scheduler.wait()

        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(18, len(resp.json()))

        self._reset_feeds_freshness(etag='jarr/fake etag')
        self.resp_headers = {'etag': '########################'}

        scheduler.run()
        scheduler.wait()

        resp = self._api('get', 'articles', data={'limit': 1000}, user='admin')
        self.assertEquals(143, len(resp.json()))
