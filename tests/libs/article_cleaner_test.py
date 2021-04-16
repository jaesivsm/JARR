import json
import unittest

from mock import patch
from requests import Response
from requests.exceptions import MissingSchema

from jarr.models.feed import Feed
from jarr.lib.enums import ArticleType
from jarr.crawler.article_builders.classic import ClassicArticleBuilder


class ConstructArticleTest(unittest.TestCase):
    response_url = '//www.pariszigzag.fr/paris-insolite-secret/'\
                   'les-plus-belles-boulangeries-de-paris'

    def setUp(self):
        module = 'jarr.crawler.article_builders.abstract.'
        self._head_patch = patch(module + 'requests.head')
        self.head_patch = self._head_patch.start()

    def tearDown(self):
        self._head_patch.stop()

    @property
    def entry(self):
        with open('tests/fixtures/article.json') as fd:
            return json.load(fd)

    @property
    def entry2(self):
        with open('tests/fixtures/article-2.json') as fd:
            return json.load(fd)

    def get_response(self, scheme='http:'):
        resp = Response()
        resp.url = scheme + self.response_url
        resp.status_code = 200
        resp.encoding = 'utf8'
        resp.headers['content-type'] = 'text/html'
        with open('tests/fixtures/article.html') as fd:
            setattr(resp, '_content', fd.read())
        return resp

    @property
    def response2(self):
        resp = Response()
        resp.status_code = 200
        resp.url = 'https://www.youtube.com/watch?v=scbrjaqM3Oc'
        resp.encoding = 'utf8'
        resp.headers['content-type'] = 'text/html'
        with open('tests/fixtures/article-2.html') as fd:
            setattr(resp, '_content', fd.read())
        return resp

    def test_missing_title(self):
        self.head_patch.return_value = self.get_response('http:')
        articles = list(ClassicArticleBuilder(Feed(id=1, user_id=1),
                                              self.entry, {}).enhance())
        self.assertEqual(1, len(articles))
        article = articles[0]
        self.assertEqual('http://www.pariszigzag.fr/?p=56413',
                         article['entry_id'])
        self.assertEqual('http:' + self.response_url, article['link'])
        self.assertEqual(1, article['user_id'])
        self.assertEqual(1, article['feed_id'])

    def test_missing_scheme(self):
        response = self.get_response('http:')
        self.head_patch.side_effect = [
                MissingSchema, MissingSchema, MissingSchema, response]
        entry = self.entry
        entry['link'] = entry['link'][5:]  # removing scheme, for testing

        articles = list(ClassicArticleBuilder(Feed(id=1, user_id=1),
                                              entry, {}).enhance())
        self.assertEqual(1, len(articles))
        article = articles[0]

        self.assertEqual(4, self.head_patch.call_count)
        self.assertEqual(response.url, self.head_patch.call_args[0][0])
        self.assertEqual('http://www.pariszigzag.fr/?p=56413',
                         article['entry_id'])
        self.assertEqual(response.url, article['link'])
        self.assertEqual(1, article['user_id'])
        self.assertEqual(1, article['feed_id'])

    def test_image_content(self):
        entry, resp = self.entry2, self.response2
        resp.headers['content-type'] = 'image/png'
        entry.pop('links')
        entry['link'] = resp.url = 'https://domain.tld/to-img.png'
        self.head_patch.return_value = resp
        articles = list(ClassicArticleBuilder(Feed(id=1, user_id=1),
                                              entry, {}).enhance())
        self.assertEqual(1, len(articles))
        article = articles[0]
        self.assertEqual(ArticleType.image, article['article_type'])

    def test_embedded_content(self):
        self.head_patch.return_value = self.response2
        articles = list(ClassicArticleBuilder(Feed(id=1, user_id=1),
                                              self.entry2, {}).enhance())
        self.assertEqual(1, len(articles))
        article = articles[0]

        self.assertEqual('yt:video:scbrjaqM3Oc', article['entry_id'])
        self.assertEqual("Ceci n'est pas Old Boy - Owlboy (suite) - "
                         "Benzaie Live", article['title'])
        self.assertEqual(1, article['user_id'])
        self.assertEqual(ArticleType.embedded, article['article_type'])
        self.assertEqual(1, article['feed_id'])

    def test_enclosure_contents(self):
        pass
