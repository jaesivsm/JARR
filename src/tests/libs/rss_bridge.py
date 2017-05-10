import unittest

from bootstrap import conf
from urllib.parse import urlsplit, parse_qs
from lib.integrations.abstract import _INTEGRATION_MAPPING
from lib.integrations.rss_bridge import InstagramIntegration
from lib.integrations import dispatch


class InstagramIntegrationTest(unittest.TestCase):
    site_links = ('http://instagram.com/jaesivsm',
                  'http://instagram.com/jaesivsm/',
                  'https://instagram.com/jaesivsm',
                  'https://instagram.com/jaesivsm/',
                  'http://www.instagram.com/jaesivsm/',
                  'https://www.instagram.com/jaesivsm/')
    link = 'https://bridge.leslibres.org/?action=display' \
           '&bridge=InstagramBridge&format=AtomFormat&u=jaesivsm'

    def setUp(self):
        conf.PLUGINS_RSS_BRIDGE = 'https://bridge.leslibres.org/'
        self.inte = InstagramIntegration()
        for inte, prio in _INTEGRATION_MAPPING:
            if isinstance(inte, InstagramIntegration):
                inte.split = urlsplit(conf.PLUGINS_RSS_BRIDGE)

    def test_match_feed_creation(self):
        self.assertFalse(self.inte.match_feed_creation({}))
        for sl in self.site_links:
            self.assertTrue(self.inte.match_feed_creation({'site_link': sl}),
                    "%s did not match" % sl)

    def test_feed_creation(self):
        original = urlsplit(self.link)
        qs = parse_qs(original.query)
        for sl in self.site_links:
            feed = {'site_link': sl}
            self.assertTrue(dispatch('feed_creation', feed))
            processed = urlsplit(feed['link'])
            self.assertEqual(processed.scheme, original.scheme)
            self.assertEqual(processed.netloc, original.netloc)
            self.assertEqual(processed.path, original.path)
            self.assertEqual(parse_qs(processed.query), qs)
