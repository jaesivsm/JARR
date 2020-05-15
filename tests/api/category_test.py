from tests.base import JarrFlaskCommon


class CategoryApiTest(JarrFlaskCommon):

    def test_NewCategoryResource_post(self):
        resp = self.jarr_client('post', 'category',
                data={'name': 'my new category'})
        self.assertStatusCode(401, resp)

        resp = self.jarr_client('post', 'category',
                data={'name': 'my new category'}, user='user1')
        self.assertStatusCode(201, resp)
        self.assertEqual('my new category', resp.json['name'])
        self.assertEqual(1, len([cat
                for cat in self.jarr_client('get', 'categories',
                    user='user1').json
                if cat['name'] == 'my new category']))

    def test_ListCategoryResource_get(self):
        resp = self.jarr_client('get', 'categories')
        self.assertStatusCode(401, resp)

        cat_u1 = self.jarr_client('get', 'categories', user='user1')
        self.assertStatusCode(200, cat_u1)

        cat_u2 = self.jarr_client('get', 'categories', user='user2')
        self.assertStatusCode(200, cat_u2)
        cat_u1 = [c['id'] for c in cat_u1.json]
        cat_u2 = [c['id'] for c in cat_u2.json]

        self.assertFalse(set(cat_u1).intersection(cat_u2))

    def test_CategoryResource_put(self):
        cat_id = self.jarr_client('get', 'categories',
                user='user1').json[0]['id']

        # testing rights and update
        resp = self.jarr_client('put', 'category', cat_id,
                data={'name': 'changed name'})
        self.assertStatusCode(401, resp)
        resp = self.jarr_client('put', 'category', cat_id,
                data={'name': 'changed name'}, user='user2')
        self.assertStatusCode(403, resp)
        resp = self.jarr_client('put', 'category', cat_id, user='user1',
                data={'name': 'changed name', 'cluster_wake_up': True})
        self.assertStatusCode(204, resp)
        cat = next(cat for cat in self.jarr_client('get', 'categories',
                user='user1').json if cat['id'] == cat_id)
        self.assertEqual('changed name', cat['name'])
        self.assertTrue(cat['cluster_wake_up'])
        resp = self.jarr_client('put', 'category', cat_id, user='user1',
                data={'cluster_enabled': False})
        self.assertStatusCode(204, resp)
        cat = next(cat for cat in self.jarr_client('get', 'categories',
                user='user1').json if cat['id'] == cat_id)
        self.assertEqual('changed name', cat['name'])
        self.assertTrue(cat['cluster_wake_up'])
        self.assertFalse(cat['cluster_enabled'])

    def test_CategoryResource_delete(self):
        cat_id = self.jarr_client('get', 'categories',
                user='user1').json[0]['id']

        resp = self.jarr_client('delete', 'category', cat_id)
        self.assertStatusCode(401, resp)
        resp = self.jarr_client('delete', 'category', cat_id, user='user2')
        self.assertStatusCode(403, resp)
        resp = self.jarr_client('delete', 'category', cat_id, user='user1')
        self.assertStatusCode(204, resp)

        categories = self.jarr_client('get', 'categories', user='user1').json
        self.assertFalse(cat_id in [cat['id'] for cat in categories])
