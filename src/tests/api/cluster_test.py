from tests.base import JarrFlaskCommon
from tests.api.common import ApiCommon


class ClusterApiTest(JarrFlaskCommon, ApiCommon):
    urn = 'cluster'
    urns = 'clusters'

    def test_api_list(self):
        resp = self._api('get', self.urns,
                         data={'order_by': '-id'},
                         user='user1')
        self.assertStatusCode(200, resp)
        self.assertEqual(9, len(resp.json()))
        self.assertTrue(resp.json()[0]['id'] > resp.json()[-1]['id'])

        resp = self._api('get', self.urns, user='user1')
        self.assertStatusCode(200, resp)
        self.assertEqual(9, len(resp.json()))

        resp = self._api('get', self.urns, data={'limit': 1}, user='user1')
        self.assertStatusCode(200, resp)
        self.assertEqual(1, len(resp.json()))

        resp = self._api('get', self.urns, user='admin')
        self.assertStatusCode(200, resp)
        self.assertEqual(10, len(resp.json()))

        resp = self._api('get', self.urns, data={'limit': 200}, user='admin')
        self.assertStatusCode(200, resp)
        self.assertEqual(18, len(resp.json()))

    def test_api_update_many(self):
        resp = self._api('put', self.urns, user='user1',
                data=[[1, {'liked': True}],
                      [2, {'read': True}]])
        self.assertEqual(['ok', 'ok'], resp.json())
        self.assertStatusCode(200, resp)
        resp = self._api('get', self.urn, 1, user='user1')
        self.assertStatusCode(200, resp)
        self.assertTrue(resp.json()['liked'])

        resp = self._api('get', self.urn, 2, user='user1')
        self.assertStatusCode(200, resp)
        self.assertTrue(resp.json()['read'])

        resp = self._api('put', self.urns, user='user1',
                data=[[1, {'liked': False}],
                      [15, {'read': True}]])
        self.assertStatusCode(206, resp)
        self.assertEqual(['ok', 'nok'], resp.json())

        resp = self._api('put', self.urns, user='user1',
                data=[[16, {'read': True}],
                      [17, {'read': True}]])
        self.assertStatusCode(500, resp)
        self.assertEqual(['nok', 'nok'], resp.json())

        resp = self._api('get', self.urn, 17, user='user1')
        self.assertStatusCode(404, resp)
