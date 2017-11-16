import unittest
from bootstrap import feed_creation

FIXED_URL = 'https://www.youtube.com/feeds/videos.xml?channel_id=<channel id>'

class YoutubeIntegrationTest(unittest.TestCase):

    def test_match_feed_creation_ok(self):
        feed = {'link': '',
                'site_link': 'http://www.youtube.com/channel/<channel id>'}
        feed_creation.send('test', feed=feed)
        self.assertEqual(feed['link'], FIXED_URL)
        self.assertEqual(feed['site_link'],
                'http://www.youtube.com/channel/<channel id>')

        feed = {'link': '',
                'site_link': 'https://www.youtube.com/channel/<channel id>'}
        feed_creation.send('test', feed=feed)
        self.assertEqual(feed['link'], FIXED_URL)

    def test_match_dispatch(self):
        feed = {'link': '',
                'site_link': 'https://www.youtube.com/channel/<channel id>'}
        feed_creation.send('test', feed=feed)
        self.assertEqual(feed['link'], FIXED_URL)
