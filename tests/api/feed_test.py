from tests.base import JarrFlaskCommon
from datetime import timezone, timedelta
from jarr.lib.utils import utc_now
from jarr.lib.enums import FeedType
from jarr.controllers import FeedController
from jarr.crawler.main import feed_cleaner


FEED = {'link': 'https://1pxsolidblack.pl/feeds/all.atom.xml',
        'site_link': 'https://1pxsolidblack.pl/',
        'title': '1pxsolidblack',
        'icon_url': 'https://1pxsolidblack.pl/img/favicon.ico'}


class FeedApiTest(JarrFlaskCommon):

    def _get(self, id_, user='user1'):
        return next(feed for feed in self.jarr_client('get', 'feeds',
                    user=user).json if feed['id'] == id_)

    @property
    def valid_filters(self):
        return [{"action": "mark as read", "pattern": " pattern ",
                 "action on": "match", "type": "simple match"}]

    def test_NewFeedResource_post(self):
        cats = self.jarr_client('get', 'categories', user='user1').json
        other_cats = self.jarr_client('get', 'categories', user='user2').json

        resp = self.jarr_client('post', 'feed',
                data={'title': 'my new feed'})
        self.assertStatusCode(401, resp)

        resp = self.jarr_client('post', 'feed',
                data={'title': 'my new feed'}, user='user1')
        self.assertStatusCode(400, resp)

        resp = self.jarr_client('post', 'feed',
                data={'title': 'my new feed', 'filters': self.valid_filters,
                      'link': 'my link'}, user='user1')
        self.assertStatusCode(201, resp)
        feed = self._get(resp.json['id'], 'user1')
        self.assertEqual(self.valid_filters, feed['filters'])
        self.assertEqual('my new feed', feed['title'])
        self.assertEqual('my link', feed['link'])

        resp = self.jarr_client('post', 'feed',
                data={'title': 'my new feed',
                      'link': 'my link', 'category_id': cats[0]['id']},
                user='user1')
        self.assertStatusCode(201, resp)

        resp = self.jarr_client('post', 'feed',
                data={'title': 'my new feed',
                      'link': 'my link', 'category_id': other_cats[0]['id']},
                user='user1')
        self.assertStatusCode(403, resp)

        feeds = self.jarr_client('get', 'feeds', user='user1').json
        self.assertEqual(1, len([feed for feed in feeds
                                 if feed['title'] == 'my new feed'
                                     and feed['category_id'] is None]))
        self.assertEqual(1, len([feed for feed in feeds
                                 if feed['title'] == 'my new feed'
                                    and feed['category_id'] == cats[0]['id']]))

    def test_ListFeedResource_get(self):
        resp = self.jarr_client('get', 'feeds')
        self.assertStatusCode(401, resp)
        feeds_u1 = self.jarr_client('get', 'feeds', user='user1').json
        feeds_u2 = self.jarr_client('get', 'feeds', user='user2').json
        feeds_u1 = [f['id'] for f in feeds_u1]
        feeds_u2 = [f['id'] for f in feeds_u2]

        self.assertFalse(set(feeds_u1).intersection(feeds_u2))

        # testing time formating
        feed = self.jarr_client('get', 'feeds', user='user1').json[0]
        now = utc_now()
        FeedController().update({'id': feed['id']}, {'last_retrieved': now})
        json = self._get(feed['id'], 'user1')
        self.assertEqual(json['last_retrieved'], now.isoformat())

        FeedController().update({'id': feed['id']},
                {'last_retrieved': now.replace(tzinfo=None)})
        json = self._get(feed['id'], 'user1')
        self.assertEqual(json['last_retrieved'], now.isoformat())

        FeedController().update({'id': feed['id']},
                {'last_retrieved':
                    now.astimezone(timezone(timedelta(hours=12)))})
        json = self._get(feed['id'], 'user1')
        self.assertEqual(json['last_retrieved'], now.isoformat())

    def test_FeedResource_put(self):
        # testing rights
        resp = self.jarr_client('put', 'feed', 1)
        self.assertStatusCode(401, resp)
        # fetching first feed
        feeds_resp = self.jarr_client('get', 'feeds', user='user1')
        self.assertStatusCode(200, feeds_resp)
        feed_id = feeds_resp.json[0]['id']
        # changing title un-logged
        resp = self.jarr_client('put', 'feed', feed_id,
                                data={'title': 'changed'})
        self.assertStatusCode(401, resp)
        # changing title wrong user
        resp = self.jarr_client('put', 'feed', feed_id,
                                data={'title': 'changed'}, user='user2')
        self.assertStatusCode(403, resp)
        # changing feed attributes
        resp = self.jarr_client('put', 'feed', feed_id,
                                data={'filters': self.valid_filters,
                                      'cluster_wake_up': True,
                                      'title': 'changed'}, user='user1')
        self.assertStatusCode(204, resp)
        feed = self.jarr_client('get', 'feed', feed_id, user='user1').json
        self.assertEqual('changed', feed['title'])
        self.assertEqual(self.valid_filters, feed['filters'])
        self.assertTrue(feed['cluster_wake_up'])
        resp = self.jarr_client('put', 'feed', feed_id,
                                data={'title': 'changed2'}, user='user1')
        self.assertStatusCode(204, resp)
        feed = self.jarr_client('get', 'feed', feed_id, user='user1').json
        self.assertTrue(feed['cluster_wake_up'])
        self.assertEqual('changed2', feed['title'])
        self.assertEqual(self.valid_filters, feed['filters'])
        # put with no change
        self.jarr_client('put', 'feed', feed_id, data={}, user='user1')
        feed = self.jarr_client('get', 'feed', feed_id, user='user1').json
        self.assertTrue(feed['cluster_wake_up'])
        self.assertEqual('changed2', feed['title'])
        self.assertEqual(self.valid_filters, feed['filters'])
        # put with limited change
        resp = self.jarr_client('put', 'feed', feed_id,
                                data={'title': 'changed again',
                                      'cluster_enabled': False}, user='user1')
        feed = self.jarr_client('get', 'feed', feed_id, user='user1').json
        self.assertTrue(feed['cluster_wake_up'])
        self.assertFalse(feed['cluster_enabled'])
        self.assertEqual('changed again', feed['title'])
        self.assertEqual(self.valid_filters, feed['filters'])
        # changing to other user category
        categories_resp = self.jarr_client('get', 'categories', user='user2')
        self.assertStatusCode(200, categories_resp)
        feed = self.jarr_client('get', 'feed', feed_id, user='user1').json
        category = categories_resp.json[0]
        resp = self.jarr_client('put', 'feed', feed_id, user='user1',
                                data={'category_id': category['id']})
        self.assertStatusCode(403, resp)

    def test_FeedResource_delete(self):
        feed_id = self.jarr_client('get', 'feeds', user='user1').json[0]['id']
        resp = self.jarr_client('delete', 'feed', feed_id)
        self.assertStatusCode(401, resp)
        resp = self.jarr_client('delete', 'feed', feed_id, user='user2')
        self.assertStatusCode(403, resp)

        resp = self.jarr_client('get', 'list-feeds', user='user1')

        self.assertTrue(any(r['type'] == 'feed' and r['id'] == feed_id
                            for r in resp.json))

        resp = self.jarr_client('delete', 'feed', feed_id, user='user1')
        self.assertStatusCode(204, resp)

        resp = self.jarr_client('get', 'list-feeds', user='user1')
        self.assertFalse(any(r['type'] == 'feed' and r['id'] == feed_id
                             for r in resp.json))

        feeds = self.jarr_client('get', 'feeds', user='user1').json
        self.assertTrue(feed_id in [feed['id'] for feed in feeds])
        self.assertEqual('to_delete', [feed['status'] for feed in feeds
                                       if feed['id'] == feed_id][0])
        feed_cleaner(feed_id)

        feeds = self.jarr_client('get', 'feeds', user='user1').json
        self.assertFalse(feed_id in [feed['id'] for feed in feeds])

        resp = self.jarr_client('get', 'list-feeds', user='user1')
        self.assertFalse(any(r['type'] == 'feed' and r['id'] == feed_id
                             for r in resp.json))

    def test_FeedBuilder_get(self):
        resp = self.jarr_client('get', 'feed', 'build')
        self.assertStatusCode(401, resp)

        resp = self.jarr_client('get', 'feed', 'build', user='user1')
        self.assertStatusCode(400, resp)

        resp = self.jarr_client('get', 'feed', 'build', user='user1',
                                data={'url': "koreus.com"})
        self.assertStatusCode(200, resp)
        self.assertEqual({
            'description': 'Koreus',
            'feed_type': FeedType.koreus.value,
            'icon_url': 'https://koreus.cdn.li/static/images/favicon.png',
            'link': 'http://feeds.feedburner.com/Koreus-articles',
            'links': ['http://feeds.feedburner.com/Koreus-articles',
                      'http://feeds.feedburner.com/Koreus-media',
                      'http://feeds.feedburner.com/Koreus-videos',
                      'http://feeds.feedburner.com/Koreus-animations',
                      'http://feeds.feedburner.com/Koreus-jeux',
                      'http://feeds.feedburner.com/Koreus-images',
                      'http://feeds.feedburner.com/Koreus-sons',
                      'http://feeds.feedburner.com/Koreus-podcasts-audio',
                      'http://feeds.feedburner.com/Koreus-podcasts-video',
                      'http://feeds.feedburner.com/Koreus-forums'],
            'same_link_count': 0,
            'site_link': 'https://www.koreus.com/',
            'title': 'Koreus.com - Articles'}, resp.json)

    def test_IconResource_get(self):
        resp = self.jarr_client('post', 'feed', user='user1', data=FEED)
        self.assertStatusCode(201, resp)
        feed = resp.json
        resp = self.jarr_client('get', 'feed', 'icon',
                                data={'url': feed['icon_url']})
        self.assertStatusCode(200, resp)
        self.assertTrue(resp.headers['Content-Type'].startswith('image/'))
