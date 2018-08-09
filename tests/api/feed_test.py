from tests.base import JarrFlaskCommon
from tests.api.common import ApiCommon
from datetime import timezone, timedelta

from jarr.controllers import UserController
from jarr_common.utils import utc_now


class FeedApiTest(JarrFlaskCommon, ApiCommon):
    urn = 'feed'
    urns = 'feeds'

    def test_api_list(self):
        resp = self._api('get', self.urns, data={'order_by': '-id'},
                         user='user1')
        self.assertStatusCode(200, resp)
        self.assertEqual(6, len(resp.json()))
        self.assertTrue(resp.json()[0]['id'] > resp.json()[-1]['id'])

        resp = self._api('get', self.urns,
                         data={'category_id': 1}, user='user1')
        self.assertStatusCode(200, resp)
        self.assertEqual(1, len(resp.json()))

        resp = self._api('get', self.urns, data={'limit': 1}, user='user1')
        self.assertStatusCode(200, resp)
        self.assertEqual(1, len(resp.json()))

        resp = self._api('get', self.urns, user='admin')
        self.assertStatusCode(200, resp)
        self.assertEqual(10, len(resp.json()))

        resp = self._api('get', self.urns, data={'limit': 200}, user='admin')
        self.assertStatusCode(200, resp)
        self.assertEqual(12, len(resp.json()))

    def test_api_update_many(self):
        resp = self._api('put', self.urns, user='user1',
                data=[[1, {'title': 'updated title 1'}],
                      [2, {'title': 'updated title 2'}]])
        self.assertStatusCode(200, resp)
        self.assertEqual(['ok', 'ok'], resp.json())

        resp = self._api('get', self.urn, 1, user='user1')
        self.assertStatusCode(200, resp)
        self.assertEqual('updated title 1', resp.json()['title'])

        resp = self._api('get', self.urn, 2, user='user1')
        self.assertStatusCode(200, resp)
        self.assertEqual('updated title 2', resp.json()['title'])

        resp = self._api('put', self.urns, user='user1',
                data=[[1, {'title': 'updated title 1'}],
                      [15, {'title': 'updated title 15'}]])
        self.assertStatusCode(206, resp)
        self.assertEqual(['ok', 'nok'], resp.json())

        resp = self._api('put', self.urns, user='user1',
                data=[[16, {'title': 'updated title 16'}],
                      [17, {'title': 'updated title 17'}]])
        self.assertStatusCode(500, resp)
        self.assertEqual(['nok', 'nok'], resp.json())

        resp = self._api('get', self.urn, 17, user='user1')
        self.assertStatusCode(404, resp)

    def test_feed_article_deletion(self):
        feed_id = self._api('get', 'feeds', user='user1').json()[0]['id']
        self._api('delete', 'feed', feed_id, user='user1')
        resp = self._api('get', 'articles',
                         data={'feed_id': feed_id}, user='user1')
        self.assertEqual(0, len(resp.json()))

    def test_feed_list_fetchable(self):
        resp = self._api('get', 'feeds/fetchable', user='user1')
        self.assertStatusCode(403, resp)
        UserController().update({'login__in': ['admin', 'user1']},
                                {'is_api': True})
        resp = self._api('get', 'feeds/fetchable', user='user1',
                         data={'limit': 100})
        self.assertStatusCode(200, resp)
        self.assertEqual(6, len(resp.json()))

        resp = self._api('get', 'feeds/fetchable', user='user1')
        self.assertStatusCode(204, resp)

        resp = self._api('get', 'feeds/fetchable', user='admin',
                         data={'limit': 100})
        self.assertStatusCode(200, resp)
        self.assertEqual(6, len(resp.json()))
        resp = self._api('get', 'feeds/fetchable', user='admin')
        self.assertStatusCode(204, resp)

    def test_api_edit_category_id(self):
        resp = self._api('get', self.urns, data={'limit': 1}, user='user1')
        self.assertStatusCode(200, resp)
        self.assertEqual(1, len(resp.json()))
        obj = resp.json()[0]
        resp = self._api('get', 'categories', data={'limit': 1}, user='user2')
        self.assertStatusCode(200, resp)
        self.assertEqual(1, len(resp.json()))
        category = resp.json()[0]
        resp = self._api('put', self.urn, obj['id'],
                         data={'category_id': category['id']}, user='user1')
        self.assertStatusCode(403, resp)

    def test_edit_time(self):
        now = utc_now()
        urn = '%s/1' % self.urn
        self._api('put', urn, user='admin',
                data={'last_retrieved': now.isoformat()})
        json = self._api('get', urn, user='admin').json()
        self.assertEqual(json['last_retrieved'], now.isoformat())

        self._api('put', urn, user='admin',
                data={'last_retrieved': now.replace(tzinfo=None).isoformat()})
        json = self._api('get', urn, user='admin').json()
        self.assertEqual(json['last_retrieved'], now.isoformat())

        self._api('put', urn, user='admin',
                data={'last_retrieved':
                    now.astimezone(timezone(timedelta(hours=12))).isoformat()})
        json = self._api('get', urn, user='admin').json()
        self.assertEqual(json['last_retrieved'], now.isoformat())
