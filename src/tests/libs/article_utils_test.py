from tests.base import JarrFlaskCommon
import json
from mock import patch
from requests.exceptions import MissingSchema
from lib.article_utils import construct_article


class ConstructArticleTest(JarrFlaskCommon):
    response_url = '//www.pariszigzag.fr/paris-insolite-secret/'\
                   'les-plus-belles-boulangeries-de-paris'

    def setUp(self):
        self._jarr_get_patch = patch('lib.article_utils.jarr_get')
        self.jarr_get_patch = self._jarr_get_patch.start()

    def tearDown(self):
        self._jarr_get_patch.stop()

    @staticmethod
    def get_entry():
        with open('src/tests/fixtures/article.json') as fd:
            return json.load(fd)

    @staticmethod
    def get_response(scheme='http:'):
        class Response:
            @property
            def url(self):
                return scheme + ConstructArticleTest.response_url

            @property
            def content(self):
                with open('src/tests/fixtures/article.html') as fd:
                    return fd.read()
        return Response()

    def test_missing_title(self):
        self.jarr_get_patch.return_value = self.get_response('http:')
        article = construct_article(self.get_entry(), {'id': 1, 'user_id': 1})
        self.assertEquals('http://www.pariszigzag.fr/?p=56413',
                          article['entry_id'])
        self.assertEquals('http:' + self.response_url, article['link'])
        self.assertEquals('Les plus belles boulangeries de Paris',
                          article['title'])
        self.assertEquals(1, article['user_id'])
        self.assertEquals(1, article['feed_id'])

    def test_missing_scheme(self):
        response = self.get_response('https:')
        self.jarr_get_patch.side_effect = [MissingSchema, response]
        entry = self.get_entry()
        entry['link'] = entry['link'][5:]

        article = construct_article(entry, {'id': 1, 'user_id': 1})

        self.assertEquals(2, self.jarr_get_patch.call_count)
        self.assertEquals(response.url, self.jarr_get_patch.call_args[0][0])
        self.assertEquals('http://www.pariszigzag.fr/?p=56413',
                          article['entry_id'])
        self.assertEquals(response.url, article['link'])
        self.assertEquals('Les plus belles boulangeries de Paris',
                          article['title'])
        self.assertEquals(1, article['user_id'])
        self.assertEquals(1, article['feed_id'])
