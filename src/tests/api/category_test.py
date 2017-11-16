from tests.base import JarrFlaskCommon
from tests.api.common import ApiCommon


class CategoryApiTest(JarrFlaskCommon, ApiCommon):
    urn = 'category'
    urns = 'categories'

    def test_api_list(self):
        resp = self._api('get', self.urns, data={'order_by': '-id'},
                         user='user1')
        self.assertStatusCode(200, resp)
        self.assertEqual(4, len(resp.json()))
        self.assertTrue(resp.json()[0]['id'] > resp.json()[-1]['id'])

        resp = self._api('get', self.urns, data={'limit': 1}, user='user1')
        self.assertStatusCode(200, resp)
        self.assertEqual(1, len(resp.json()))

        resp = self._api('get', self.urns, user='admin')
        self.assertStatusCode(200, resp)
        self.assertEqual(8, len(resp.json()))

        resp = self._api('get', self.urns, data={'limit': 200}, user='admin')
        self.assertStatusCode(200, resp)
        self.assertEqual(8, len(resp.json()))

    def test_creation(self):
        resp = self._api('post', self.urn, data={'name': 'test'}, user='user1')
        self.assertStatusCode(201, resp)
        self.assertEqual('test', resp.json()['name'])

    def test_api_update_many(self):
        resp = self._api('put', self.urns, user='user1',
                data=[[1, {'name': 'updated name 1'}],
                      [2, {'name': 'updated name 2'}]])
        self.assertStatusCode(200, resp)
        self.assertEqual(['ok', 'ok'], resp.json())

        resp = self._api('get', self.urn, 1, user='user1')
        self.assertStatusCode(200, resp)
        self.assertEqual('updated name 1', resp.json()['name'])

        resp = self._api('get', self.urn, 2, user='user1')
        self.assertStatusCode(200, resp)
        self.assertEqual('updated name 2', resp.json()['name'])

        resp = self._api('put', self.urns, user='user1',
                data=[[1, {'name': 'updated name 1'}],
                      [3, {'name': 'updated name 3'}]])
        self.assertStatusCode(206, resp)
        self.assertEqual(['ok', 'nok'], resp.json())

        resp = self._api('put', self.urns, user='user1',
                data=[[3, {'name': 'updated name 3'}],
                      [4, {'name': 'updated name 4'}]])
        self.assertStatusCode(500, resp)
        self.assertEqual(['nok', 'nok'], resp.json())

        resp = self._api('get', self.urn, 3, user='user1')
        self.assertStatusCode(404, resp)
