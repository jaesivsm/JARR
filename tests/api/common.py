class ApiCommon:
    urn = None
    urns = None

    def test_api_rights(self):
        self.assertStatusCode(401, self._api('get', self.urn, 1))
        log_failed_resp = self._api('get', self.urn, 1, user='donotexist')
        self.assertStatusCode(403, log_failed_resp)
        resp = self._api('get', self.urn, 1, user='user1')
        self.assertStatusCode(200, resp)

        resp = self._api('put', self.urn, 1, data={'user_id': 3}, user='user1')
        self.assertStatusCode(400, resp)
        resp = self._api('put', self.urn, 1, data={'user_id': 3}, user='admin')
        self.assertStatusCode(200, resp)
        resp = self._api('get', self.urn, 1, user='user1')
        self.assertStatusCode(404, resp)
        resp = self._api('get', self.urn, 1, user='user2')
        self.assertStatusCode(200, resp)

        resp = self._api('put', self.urns, user='user1',
                data=[[1, {'nonexisting': 'nonexisting'}],
                      [2, {'user_id': 'Unauthorized'}]])
        self.assertStatusCode(500, resp)
        self.assertEqual(['attributes to update must not be empty',
                          'attributes to update must not be empty'],
                          resp.json())

    def test_api_delete(self):
        resp = self._api('delete', self.urn, 1, user='user1')
        self.assertStatusCode(204, resp)

    def test_api_delete_many(self):
        resp = self._api('delete', self.urns, data=[1, 30], user='user1')
        self.assertStatusCode(206, resp)
        self.assertEqual(["ok", "404: Not Found"], resp.json())

        resp = self._api('delete', self.urns, data=[2], user='user1')
        self.assertStatusCode(204, resp)

        resp = self._api('delete', self.urns, data=[110, 120], user='user1')
        self.assertStatusCode(500, resp)

    def test_api_edit_user_id(self):
        resp = self._api('get', self.urns, data={'limit': 1}, user='user1')
        self.assertStatusCode(200, resp)
        objs = resp.json()
        self.assertEqual(1, len(objs))
        obj = objs[0]
        resp = self._api('put', self.urn, obj['id'], data={'user_id': 3})
        self.assertStatusCode(400, resp)
