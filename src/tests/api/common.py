class ApiCommon:
    urn = None
    urns = None

    def test_api_rights(self):
        self.assertEquals(401, self._api('get', self.urn, 1).status_code)
        log_failed_resp = self._api('get', self.urn, 1, user='donotexist')
        self.assertEquals(403, log_failed_resp.status_code)
        resp = self._api('get', self.urn, 1, user='user1')
        self.assertEquals(200, resp.status_code)

        resp = self._api('put', self.urn, 1, data={'user_id': 3}, user='user1')
        self.assertEquals(400, resp.status_code)
        resp = self._api('put', self.urn, 1, data={'user_id': 3}, user='admin')
        self.assertEquals(200, resp.status_code)
        resp = self._api('get', self.urn, 1, user='user1')
        self.assertEquals(404, resp.status_code)
        resp = self._api('get', self.urn, 1, user='user2')
        self.assertEquals(200, resp.status_code)

        resp = self._api('put', self.urns, user='user1',
                data=[[1, {'nonexisting': 'nonexisting'}],
                      [2, {'user_id': 'Unauthorized'}]])
        self.assertEquals(['attributes to update must not be empty',
                           'attributes to update must not be empty'],
                          resp.json())
        self.assertEquals(500, resp.status_code)

    def test_api_delete(self):
        resp = self._api('delete', self.urn, 1, user='user1')
        self.assertEquals(204, resp.status_code)

    def test_api_delete_many(self):
        resp = self._api('delete', self.urns, data=[1, 30], user='user1')
        self.assertEquals(206, resp.status_code)
        self.assertEquals(["ok", "404: Not Found"], resp.json())

        resp = self._api('delete', self.urns, data=[2], user='user1')
        self.assertEquals(204, resp.status_code)

        resp = self._api('delete', self.urns, data=[110, 120], user='user1')
        self.assertEquals(500, resp.status_code)

    def test_api_edit_user_id(self):
        resp = self._api('get', self.urns, data={'limit': 1}, user='user1')
        self.assertEquals(200, resp.status_code)
        objs = resp.json()
        self.assertEquals(1, len(objs))
        obj = objs[0]
        resp = self._api('put', self.urn, obj['id'], data={'user_id': 3})
        self.assertEquals(400, resp.status_code)
