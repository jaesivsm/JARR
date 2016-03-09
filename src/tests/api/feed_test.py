from tests.base import JarrFlaskCommon
from tests.api.common import ApiCommon
from web.controllers import UserController


class FeedApiTest(JarrFlaskCommon, ApiCommon):
    urn = 'feed'
    urns = 'feeds'

    def test_api_list(self):
        resp = self._api('get', self.urns, data={'order_by': '-id'},
                         user='user1')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(3, len(resp.json()))
        self.assertTrue(resp.json()[0]['id'] > resp.json()[-1]['id'])

        resp = self._api('get', self.urns,
                         data={'category_id': 1}, user='user1')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(1, len(resp.json()))

        resp = self._api('get', self.urns, data={'limit': 1}, user='user1')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(1, len(resp.json()))

        resp = self._api('get', self.urns, user='admin')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(6, len(resp.json()))

        resp = self._api('get', self.urns, data={'limit': 200}, user='admin')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(6, len(resp.json()))

    def test_api_update_many(self):
        resp = self._api('put', self.urns, user='user1',
                data=[[1, {'title': 'updated title 1'}],
                      [2, {'title': 'updated title 2'}]])
        self.assertEquals(200, resp.status_code)
        self.assertEquals(['ok', 'ok'], resp.json())

        resp = self._api('get', self.urn, 1, user='user1')
        self.assertEquals(200, resp.status_code)
        self.assertEquals('updated title 1', resp.json()['title'])

        resp = self._api('get', self.urn, 2, user='user1')
        self.assertEquals(200, resp.status_code)
        self.assertEquals('updated title 2', resp.json()['title'])

        resp = self._api('put', self.urns, user='user1',
                data=[[1, {'title': 'updated title 1'}],
                      [15, {'title': 'updated title 15'}]])
        self.assertEquals(206, resp.status_code)
        self.assertEquals(['ok', 'nok'], resp.json())

        resp = self._api('put', self.urns, user='user1',
                data=[[16, {'title': 'updated title 16'}],
                      [17, {'title': 'updated title 17'}]])
        self.assertEquals(500, resp.status_code)
        self.assertEquals(['nok', 'nok'], resp.json())

        resp = self._api('get', self.urn, 17, user='user1')
        self.assertEquals(404, resp.status_code)

    def test_feed_article_deletion(self):
        feed_id = self._api('get', 'feeds', user='user1').json()[0]['id']
        self._api('delete', 'feed', feed_id, user='user1')
        resp = self._api('get', 'articles',
                         data={'feed_id': feed_id}, user='user1')
        self.assertEquals(0, len(resp.json()))

    def test_feed_list_fetchable(self):
        resp = self._api('get', 'feeds/fetchable', user='user1')
        self.assertEquals(403, resp.status_code)
        UserController().update({'login__in': ['admin', 'user1']},
                                {'is_api': True})
        resp = self._api('get', 'feeds/fetchable', user='user1')
        self.assertEquals(3, len(resp.json()))
        self.assertEquals(200, resp.status_code)

        resp = self._api('get', 'feeds/fetchable', user='user1')
        self.assertEquals(204, resp.status_code)

        resp = self._api('get', 'feeds/fetchable', user='admin')
        self.assertEquals(3, len(resp.json()))
        self.assertEquals(200, resp.status_code)
        resp = self._api('get', 'feeds/fetchable', user='admin')
        self.assertEquals(204, resp.status_code)

        resp = self._api('get', 'feeds/fetchable', user='user1',
                         data={'refresh_rate': 0})
        self.assertEquals(3, len(resp.json()))
        resp = self._api('get', 'feeds/fetchable', user='admin',
                         data={'refresh_rate': 0})
        self.assertEquals(5, len(resp.json()))

    def test_api_edit_category_id(self):
        resp = self._api('get', self.urns, data={'limit': 1}, user='user1')
        self.assertEquals(1, len(resp.json()))
        self.assertEquals(200, resp.status_code)
        obj = resp.json()[0]
        resp = self._api('get', 'categories', data={'limit': 1}, user='user2')
        self.assertEquals(1, len(resp.json()))
        self.assertEquals(200, resp.status_code)
        category = resp.json()[0]
        resp = self._api('put', self.urn, obj['id'],
                         data={'category_id': category['id']}, user='user1')
        self.assertEquals(400, resp.status_code)
