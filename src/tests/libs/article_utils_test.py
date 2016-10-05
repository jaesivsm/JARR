from tests.base import JarrFlaskCommon
import json
from mock import patch
from lib.article_utils import construct_article


class ConstructArticleTest(JarrFlaskCommon):

    @patch('lib.article_utils.jarr_get')
    def test_missing_title(self, jarr_get):
        class Response:
            @property
            def url(self):
                return 'http://www.pariszigzag.fr/paris-insolite-secret/'\
                        'les-plus-belles-boulangeries-de-paris'
            @property
            def content(self):
                with open('src/tests/fixtures/article.html') as fd:
                    return fd.read()
        jarr_get.return_value = Response()
        with open('src/tests/fixtures/article.json') as fd:
            entry = json.load(fd)

        article = construct_article(entry, {'id': 1, 'user_id': 1})
        self.assertEquals('http://www.pariszigzag.fr/?p=56413',
                          article['entry_id'])
        self.assertEquals(Response().url, article['link'])
        self.assertEquals('Les plus belles boulangeries de Paris',
                          article['title'])
        self.assertEquals(1, article['user_id'])
        self.assertEquals(1, article['feed_id'])
