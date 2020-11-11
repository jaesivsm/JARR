import unittest

from jarr.crawler.article_builders.rss_bridge import (
    RSSBridgeArticleBuilder, RSSBridgeTwitterArticleBuilder)
from jarr.models.feed import Feed


class RSSBridgeIntegrationTest(unittest.TestCase):

    def test_skip_entry(self):
        feed = Feed(link='https://a.random.url/')
        entry = {'title': 'Bridge returned error for unknown reason'}
        self.assertFalse(RSSBridgeArticleBuilder(feed, entry).do_skip_creation)
        entry = {'title': 'Any other title'}
        self.assertTrue(RSSBridgeArticleBuilder(feed, entry).do_skip_creation)
