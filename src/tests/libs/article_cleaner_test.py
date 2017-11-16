import json
import unittest

from mock import patch
from requests import Response
from requests.exceptions import MissingSchema

from lib.clustering_af.word_utils import FakeStemmer
from lib.article_utils import construct_article


class ConstructArticleTest(unittest.TestCase):
    response_url = '//www.pariszigzag.fr/paris-insolite-secret/'\
                   'les-plus-belles-boulangeries-de-paris'

    def setUp(self):
        self._jarr_get_patch = patch('lib.article_utils.jarr_get')
        self.jarr_get_patch = self._jarr_get_patch.start()

    def tearDown(self):
        self._jarr_get_patch.stop()

    @property
    def entry(self):
        with open('src/tests/fixtures/article.json') as fd:
            return json.load(fd)

    @property
    def entry2(self):
        with open('src/tests/fixtures/article-2.json') as fd:
            return json.load(fd)

    @staticmethod
    def get_response(scheme='http:'):
        resp = Response()
        resp.url = scheme + ConstructArticleTest.response_url
        resp.encoding = 'utf8'
        with open('src/tests/fixtures/article.html') as fd:
            resp._content = fd.read()
        return resp

    @property
    def response2(self):
        resp = Response()
        resp.url = 'https://www.youtube.com/watch?v=scbrjaqM3Oc'
        resp.encoding = 'utf8'
        with open('src/tests/fixtures/article-2.html') as fd:
            resp._content = fd.read()
        return resp

    def test_missing_title(self):
        self.jarr_get_patch.return_value = self.get_response('http:')
        article = construct_article(self.entry, {'id': 1, 'user_id': 1})
        self.assertEqual('http://www.pariszigzag.fr/?p=56413',
                          article['entry_id'])
        self.assertEqual('http:' + self.response_url, article['link'])
        self.assertEqual('Les plus belles boulangeries de Paris',
                          article['title'])
        self.assertEqual(1, article['user_id'])
        self.assertEqual(1, article['feed_id'])

    def test_missing_scheme(self):
        response = self.get_response('http:')
        self.jarr_get_patch.side_effect = [
                MissingSchema, MissingSchema, response]
        entry = self.entry
        entry['link'] = entry['link'][5:]

        article = construct_article(entry, {'id': 1, 'user_id': 1})

        self.assertEqual(3, self.jarr_get_patch.call_count)
        self.assertEqual(response.url, self.jarr_get_patch.call_args[0][0])
        self.assertEqual('http://www.pariszigzag.fr/?p=56413',
                          article['entry_id'])
        self.assertEqual(response.url, article['link'])
        self.assertEqual('Les plus belles boulangeries de Paris',
                          article['title'])
        self.assertEqual(1, article['user_id'])
        self.assertEqual(1, article['feed_id'])

    @patch('lib.clustering_af.word_utils.get_stemmer')
    @patch('lib.clustering_af.word_utils.get_stopwords')
    def test_tags(self, get_stopwords, get_stemmer):
        get_stemmer.return_value = FakeStemmer()
        get_stopwords.return_value = []
        import bootstrap
        bootstrap.conf.CRAWLER_RESOLV = True
        self.jarr_get_patch.return_value = self.response2
        article = construct_article(self.entry2, {'id': 1, 'user_id': 1})

        print(article['valuable_tokens'])
        self.assertEqual(sorted(['ceci', 'est', 'pas', 'old', 'boy', 'owlboy',
                                  'suite', 'benzaie', 'live', 'watch', 'live',
                                  'at', 'games', 'twitch']),
                          sorted(article['valuable_tokens']))

        self.assertEqual('yt:video:scbrjaqM3Oc', article['entry_id'])
        self.assertEqual(self.response2.url, article['link'])
        self.assertEqual("Ceci n'est pas Old Boy - Owlboy (suite) - "
                          "Benzaie Live", article['title'])
        self.assertEqual(1, article['user_id'])
        self.assertEqual(1, article['feed_id'])
        self.assertEqual({'twitch', 'games'}, article['tags'])
