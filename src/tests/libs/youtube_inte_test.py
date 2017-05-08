import unittest

from mock import patch, Mock

from bootstrap import conf
from lib.integrations.youtube import YoutubeIntegration
from lib.integrations import dispatch

FIXED_URL = 'https://www.youtube.com/feeds/videos.xml?channel_id=<channel id>'

class YoutubeIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.inte = YoutubeIntegration()

    def test_match_feed_creation(self):
        self.assertFalse(self.inte.match_feed_creation({}))

    def test_match_entry_parsing(self):
        self.assertFalse(self.inte.match_entry_parsing({}, {}))

    def test_match_article_parsing(self):
        self.assertFalse(self.inte.match_article_parsing({}, {}, {}))

    def test_match_feed_creation_ok(self):
        self.assertTrue(self.inte.match_feed_creation({'link': '',
                'site_link': 'http://www.youtube.com/channel/<channel id>'}))
        self.assertTrue(self.inte.match_feed_creation({'link': '',
                'site_link': 'https://www.youtube.com/channel/<channel id>'}))

        feed = {'link': '',
                'site_link': 'https://www.youtube.com/channel/<channel id>'}
        self.assertTrue(self.inte.feed_creation(feed))
        self.assertEqual(feed['link'], FIXED_URL)

    def test_match_dispatch(self):
        feed = {'link': '',
                'site_link': 'https://www.youtube.com/channel/<channel id>'}
        self.assertTrue(dispatch('feed_creation', feed))
        self.assertEqual(feed['link'], FIXED_URL)
