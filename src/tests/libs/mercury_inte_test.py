import unittest

from mock import patch, Mock

from bootstrap import article_parsing

SAMPLE = """<a href="link_to_correct.html">
<img src="http://is_ok.com/image"/>
</a>
<a href="http://is_also_ok.fr/link">test</a>
<iframe src="http://youtube.com/an_unsecure_video">
</iframe>
<img src="http://abs.ol/ute/buggy.img%2C%20otherbuggy.img" srcset="garbage"/>
<img src="relative.img" />"""


class MercuryIntegrationTest(unittest.TestCase):

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
        # should not raise
        user, feed, cluster = self.base_objs
        article_parsing.send('test', user=user, feed=feed, cluster=cluster)
        self.assertFalse('content' in cluster.main_article)

        article_parsing.send('test', user=user, feed=feed, cluster=cluster,
                             mercury_may_parse=True)
        self.assertFalse('content' in cluster.main_article)

        user.readability_key = 'True'
        article_parsing.send('test', user=user, feed=feed, cluster=cluster,
                             mercury_may_parse=True)
        self.assertFalse('content' in cluster.main_article)

        article_parsing.send('test', user=user, feed=feed, cluster=cluster,
                             mercury_may_parse=True, mercury_parse=True)
        self.assertFalse('content' in cluster.main_article)

    @patch('lib.integrations.mercury.jarr_get')
    @patch('lib.integrations.mercury.flash')
    @patch('lib.integrations.mercury.ArticleController')
    def test_parsing(self, artc, flash, jarr_get):
        jarr_get.return_value.json.return_value = {}
        user, feed, cluster = self.base_objs
        user.readability_key = 'True'
        cluster.main_article.readability_parsed = False
        cluster.main_article['readability_parsed'] = False

        article_parsing.send('test', user=user, feed=feed, cluster=cluster,
                             mercury_may_parse=True, mercury_parse=True)
        self.assertEqual('Mercury responded with {}(1)', flash.call_args[0][0])
        self.assertFalse(cluster.main_article['readability_parsed'])

        jarr_get.return_value.json.return_value = {'garbage': 'garbage'}
        article_parsing.send('test', user=user, feed=feed, cluster=cluster,
                             mercury_may_parse=True, mercury_parse=True)
        self.assertEqual('Mercury responded without content',
                         flash.call_args[0][0])
        self.assertFalse(cluster.main_article['readability_parsed'])

        jarr_get.return_value.json.return_value = {'content': 'content'}
        article_parsing.send('test', user=user, feed=feed, cluster=cluster,
                             mercury_may_parse=True, mercury_parse=True)
        self.assertEqual('content', cluster.main_article['content'])
        self.assertTrue(cluster.main_article['readability_parsed'])
