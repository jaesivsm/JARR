from tests.base import JarrFlaskCommon
from tests.api.common import ApiCommon
from web.controllers import UserController


class ArticleApiTest(JarrFlaskCommon, ApiCommon):
    urn = 'article'
    urns = 'articles'

    def test_api_list(self):
        resp = self._api('get', self.urns,
                         data={'feed_id': 1, 'order_by': '-id'},
                         user='user1')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(3, len(resp.json()))
        self.assertTrue(resp.json()[0]['id'] > resp.json()[-1]['id'])

        resp = self._api('get', self.urns,
                         data={'category_id': 1}, user='user1')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(3, len(resp.json()))

        resp = self._api('get', self.urns, data={'limit': 1}, user='user1')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(1, len(resp.json()))

        resp = self._api('get', self.urns, user='admin')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(10, len(resp.json()))

        resp = self._api('get', self.urns, data={'limit': 200}, user='admin')
        self.assertEquals(200, resp.status_code)
        self.assertEquals(18, len(resp.json()))

    def test_api_update_many(self):
        resp = self._api('put', self.urns, user='user1',
                data=[[1, {'like': True}],
                      [2, {'readed': True}]])
        self.assertEquals(['ok', 'ok'], resp.json())
        self.assertEquals(200, resp.status_code)
        resp = self._api('get', self.urn, 1, user='user1')
        self.assertEquals(200, resp.status_code)
        self.assertTrue(resp.json()['like'])

        resp = self._api('get', self.urn, 2, user='user1')
        self.assertEquals(200, resp.status_code)
        self.assertTrue(resp.json()['readed'])

        resp = self._api('put', self.urns, user='user1',
                data=[[1, {'like': False}],
                      [15, {'readed': True}]])
        self.assertEquals(206, resp.status_code)
        self.assertEquals(['ok', 'nok'], resp.json())

        resp = self._api('put', self.urns, user='user1',
                data=[[16, {'readed': True}],
                      [17, {'readed': True}]])
        self.assertEquals(500, resp.status_code)
        self.assertEquals(['nok', 'nok'], resp.json())

        resp = self._api('get', self.urn, 17, user='user1')
        self.assertEquals(404, resp.status_code)

    def test_article_challenge_method(self):
        articles = self._api('get', self.urns, user='user1').json()
        UserController().update({'login__in': ['admin', 'user2']},
                                {'is_api': True})
        # admin knows this article (he knows them all)
        resp = self._api('get', 'articles/challenge', user='admin',
                data={'ids': [{'id': art['id']} for art in articles]})
        self.assertEquals(204, resp.status_code)
        # admin knows this article (he knows them all)
        resp = self._api('get', 'articles/challenge', user='admin',
                data={'ids': [{'id': art['id']} for art in articles]})
        self.assertEquals(204, resp.status_code)
        # user2 doesn't know user1 article, will consider them as knew
        resp = self._api('get', 'articles/challenge', user='user2',
                data={'ids': [{'id': art['id']} for art in articles]})
        self.assertEquals(9, len(resp.json()))
        # fake ids won't be recognised either and considered as new
        resp = self._api('get', 'articles/challenge', user='user2',
                data={'ids': [{'entry_id': art['id']} for art in articles]})
        self.assertEquals(9, len(resp.json()))

    def test_api_creation(self):
        resp = self._api('post', self.urn, user='user1', data={'feed_id': 1})
        self.assertEquals(403, resp.status_code)
        UserController().update({'login': 'user1'}, {'is_api': True})
        resp = self._api('post', self.urn, user='user1', data={'feed_id': 1})
        self.assertEquals(201, resp.status_code)
        self.assertEquals(2, resp.json()['user_id'])
        resp = self._api('post', self.urn, user='user1', data={'feed_id': 1})
        self.assertEquals(2, resp.json()['user_id'])
        self.assertEquals(201, resp.status_code)
        resp = self._api('post', self.urn, user='user2',
                data={'user_id': 2, 'feed_id': 1})
        self.assertEquals(403, resp.status_code)
        UserController().update({'login': 'user2'}, {'is_api': True})
        resp = self._api('post', self.urn, user='user2',
                data={'user_id': 2, 'feed_id': 1})
        self.assertEquals(404, resp.status_code)

        resp = self._api('post', self.urns, user='user1',
                data=[{'feed_id': 1}, {'feed_id': 5}])
        self.assertEquals(206, resp.status_code)
        self.assertTrue(isinstance(resp.json()[0], dict))
        self.assertEquals('404: Not Found', resp.json()[1])

        resp = self._api('post', self.urns, user='user1',
                data=[{'user_id': 1, 'feed_id': 6}, {'feed_id': 5}])
        self.assertEquals(500, resp.status_code)
        self.assertEquals(['404: Not Found', '404: Not Found'], resp.json())

    def test_api_edit_feed_id(self):
        resp = self._api('get', self.urns, data={'limit': 1}, user='user1')
        self.assertEquals(1, len(resp.json()))
        self.assertEquals(200, resp.status_code)
        obj = resp.json()[0]
        resp = self._api('get', 'feeds', data={'limit': 1}, user='user2')
        self.assertEquals(1, len(resp.json()))
        self.assertEquals(200, resp.status_code)
        feed = resp.json()[0]
        resp = self._api('put', self.urn, obj['id'], user='user1',
                         data={'feed_id': feed['id']})
        self.assertEquals(400, resp.status_code)

    def test_api_edit_category_id(self):
        resp = self._api('get', self.urns, data={'limit': 1}, user='user1')
        self.assertEquals(1, len(resp.json()))
        self.assertEquals(200, resp.status_code)
        obj = resp.json()[0]
        resp = self._api('get', 'categories', data={'limit': 1}, user='user2')
        self.assertEquals(1, len(resp.json()))
        self.assertEquals(200, resp.status_code)
        category = resp.json()[0]
        resp = self._api('put', self.urn, obj['id'], user='user1',
                         data={'category_id': category['id']})
        self.assertEquals(400, resp.status_code)
