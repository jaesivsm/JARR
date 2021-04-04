import json
import unittest

from mock import patch

from jarr.crawler.article_builders.rss_bridge import (
    RSSBridgeArticleBuilder, RSSBridgeTwitterArticleBuilder)
from jarr.models.feed import Feed


class RSSBridgeIntegrationTest(unittest.TestCase):

    def setUp(self):
        module = 'jarr.crawler.article_builders.abstract.'
        self._head_patch = patch(module + 'requests.head')
        self.head_patch = self._head_patch.start()
        self.head_patch.return_value = None
        self.feed = Feed(link='https://a.random.url/')

    def tearDown(self):
        self._head_patch.stop()

    def test_skip_entry(self):
        entry = {'title': 'Bridge returned error for unknown reason'}
        builder = RSSBridgeArticleBuilder(self.feed, entry)
        self.assertTrue(builder.do_skip_creation)
        builder = RSSBridgeArticleBuilder(self.feed, {'title': 'Any other'})
        self.assertFalse(builder.do_skip_creation)

    def test_rss_twitter_bridge_link_handling(self):
        with open('tests/fixtures/link_tweet.json') as fd:
            entry = json.load(fd)
        builder = RSSBridgeTwitterArticleBuilder(self.feed, entry)
        self.assertEqual(entry['link'], builder.article['link'])
        articles = list(builder.enhance())
        self.assertEqual(1, len(articles))
        article = articles[0]
        self.assertEqual("https://www.enercoop.fr/content/licoornes-les-cooper"
                         "atives-du-monde-dapres", article['link'])
        self.assertEqual(entry['link'], article['comments'])
        self.assertIsNone(article.get('article_type'))

    def test_rss_twitter_bridge_img_handling(self):
        with open('tests/fixtures/img_tweet.json') as fd:
            entry = json.load(fd)
        builder = RSSBridgeTwitterArticleBuilder(self.feed, entry)
        self.assertEqual(entry['link'], builder.article['link'])
        articles = list(builder.enhance())
        self.assertEqual(2, len(articles))
        self.assertTrue(any("https://pbs.twimg.com/media/EmZUUQxXcAAxMTp.jpg"
                            in article['link'] for article in articles))
        self.assertTrue(any(entry['link'] == article['comments']
                            for article in articles))
        self.assertTrue(any('image' == article['article_type'].value
                            for article in articles))
