import unittest

from mock import patch, Mock

from bootstrap import conf
from lib.integrations.mercury import MercuryIntegration

SAMPLE = """<a href="link_to_correct.html">
<img src="http://is_ok.com/image"/>
</a>
<a href="http://is_also_ok.fr/link">test</a>
<iframe src="http://youtube.com/an_unsecure_video">
</iframe>
<img src="http://abs.ol/ute/buggy.img%2C%20otherbuggy.img" srcset="garbage"/>
<img src="relative.img" />"""


class MercuryIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.inte = MercuryIntegration()

    def test_match_feed_creation(self):
        self.assertFalse(self.inte.match_feed_creation({}))

    def test_match_entry_parsing(self):
        self.assertFalse(self.inte.match_entry_parsing({}, {}))

    @property
    def base_objs(self):
        user = Mock(readability_key=False)
        feed = Mock(readability_auto_parse=True)

        class Article(dict):
            id, link, readability_parsed = 1, 'http://whatever.com/', True
        cluster = Mock()
        cluster.main_article = Article()
        cluster.main_article['readability_parsed'] = True
        return user, feed, cluster

    def test_match_article_parsing(self):
        self.assertFalse(self.inte.match_article_parsing(
                None, None, None, mercury_may_parse=False))

        user, feed, cluster = self.base_objs

        self.assertFalse(self.inte.match_article_parsing(
                user, feed, cluster, mercury_may_parse=True))

        user.readability_key = True

        self.assertFalse(self.inte.match_article_parsing(
                user, feed, cluster, mercury_may_parse=True))

        cluster.main_article.readability_parsed = False

        self.assertTrue(self.inte.match_article_parsing(
                user, feed, cluster, mercury_may_parse=True))

        feed.readability_auto_parse = False

        self.assertTrue(self.inte.match_article_parsing(user, feed, cluster,
                mercury_may_parse=True, mercury_parse=True))

        self.assertFalse(self.inte.match_article_parsing(
                user, feed, cluster, mercury_may_parse=True))

    @patch('lib.integrations.mercury.jarr_get')
    @patch('lib.integrations.mercury.flash')
    def test_parsing(self, flash, jarr_get):
        self.inte._get_article_controller = Mock()
        jarr_get.return_value.json.return_value = {}
        user, feed, cluster = self.base_objs
        cluster.main_article['readability_parsed'] = False
        self.assertEqual(cluster.main_article,
                         self.inte.article_parsing(user, feed, cluster))
        self.assertEqual('Mercury responded with {}(1)', flash.call_args[0][0])
        self.assertFalse(cluster.main_article['readability_parsed'])

        jarr_get.return_value.json.return_value = {'garbage': 'garbage'}
        self.assertEqual(cluster.main_article,
                         self.inte.article_parsing(user, feed, cluster))
        self.assertEqual('Mercury responded without content',
                         flash.call_args[0][0])
        self.assertFalse(cluster.main_article['readability_parsed'])

        jarr_get.return_value.json.return_value = {'content': 'content'}
        new_article = self.inte.article_parsing(user, feed, cluster)
        self.assertEqual('content', new_article['content'])
        self.assertEqual('content', cluster.main_article['content'])
        self.assertTrue(cluster.main_article['readability_parsed'])
