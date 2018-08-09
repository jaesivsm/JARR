import unittest
from urllib.parse import urlsplit, parse_qs
from jarr.bootstrap import conf, feed_creation


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
        conf.plugins.rss_bridge = 'https://bridge.leslibres.org/'

    def test_feed_creation(self):
        original = urlsplit(self.link)
        original_qs = parse_qs(original.query)
        for sl in self.site_links:
            feed = {'site_link': sl}
            feed_creation.send('test', feed=feed)
            processed = urlsplit(feed['link'])
            self.assertEqual(processed.scheme, original.scheme)
            self.assertEqual(processed.netloc, original.netloc)
            self.assertEqual(processed.path, original.path)
            parsed_qs = parse_qs(processed.query)
            self.assertEqual(parsed_qs, original_qs)
            self.assertEqual(parsed_qs.get('format'), ['AtomFormat'])
            self.assertEqual(parsed_qs.get('bridge'), ['InstagramBridge'])
            self.assertEqual(parsed_qs.get('u'), ['jaesivsm'])
