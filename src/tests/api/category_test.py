from tests.base import JarrFlaskCommon
from tests.api.common import ApiCommon


class CategoryApiTest(JarrFlaskCommon, ApiCommon):
    urn = 'category'
    urns = 'categories'

    def test_api_list(self):
        resp = self._api('get', self.urns, data={'order_by': '-id'},
                         user='user1')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(4, len(resp.json()))
        self.assertTrue(resp.json()[0]['id'] > resp.json()[-1]['id'])

        resp = self._api('get', self.urns, data={'limit': 1}, user='user1')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(1, len(resp.json()))

        resp = self._api('get', self.urns, user='admin')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(8, len(resp.json()))

        resp = self._api('get', self.urns, data={'limit': 200}, user='admin')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(8, len(resp.json()))

    def test_api_update_many(self):
        resp = self._api('put', self.urns, user='user1',
                data=[[1, {'name': 'updated name 1'}],
                      [2, {'name': 'updated name 2'}]])
        self.assertEquals(200, resp.status_code)
        self.assertEquals(['ok', 'ok'], resp.json())

        resp = self._api('get', self.urn, 1, user='user1')
        self.assertEquals(200, resp.status_code)
        self.assertEquals('updated name 1', resp.json()['name'])

        resp = self._api('get', self.urn, 2, user='user1')
        self.assertEquals(200, resp.status_code)
        self.assertEquals('updated name 2', resp.json()['name'])

        resp = self._api('put', self.urns, user='user1',
                data=[[1, {'name': 'updated name 1'}],
                      [3, {'name': 'updated name 3'}]])
        self.assertEquals(206, resp.status_code)
        self.assertEquals(['ok', 'nok'], resp.json())

        resp = self._api('put', self.urns, user='user1',
                data=[[3, {'name': 'updated name 3'}],
                      [4, {'name': 'updated name 4'}]])
        self.assertEquals(500, resp.status_code)
        self.assertEquals(['nok', 'nok'], resp.json())

        resp = self._api('get', self.urn, 3, user='user1')
        self.assertEquals(404, resp.status_code)
