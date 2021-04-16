import unittest

from mock import patch
from requests import Response

from jarr.lib.html_parsing import (extract_feed_links, extract_icon_url,
                                   extract_title)


class HTMLParsingTest(unittest.TestCase):

    @property
    def article(self):
        resp = Response()
        resp.url = 'http://www.pariszigzag.fr/paris-insolite-secret/'\
                   'les-plus-belles-boulangeries-de-paris'
        resp.encoding = 'utf8'
        with open('tests/fixtures/article.html', 'rb') as fd:
            setattr(resp, '_content', fd.read())
        return resp

    @property
    def article2(self):
        resp = Response()
        resp.url = 'https://www.youtube.com/watch?v=scbrjaqM3Oc'
        resp.encoding = 'utf8'
        with open('tests/fixtures/article-2.html', 'rb') as fd:
            setattr(resp, '_content', fd.read())
        return resp

    def test_extract_title(self):
        self.assertEqual('Les plus belles boulangeries de Paris',
                         extract_title(self.article))
        self.assertEqual("Ceci n'est pas Old Boy - Owlboy (suite) "
                         "- Benzaie Live", extract_title(self.article2))

    def test_extract_feed_links(self):
        self.assertEqual(self.article.url + '/feed',
                         list(extract_feed_links(self.article))[0])

        yt_feed_link = 'http://www.youtube.com/oembed?url=https%3A%2F%2F'\
                       'www.youtube.com%2Fwatch%3Fv%3DscbrjaqM3Oc&format=json'
        self.assertEqual(yt_feed_link,
                         list(extract_feed_links(self.article2))[0])

    @patch('jarr.lib.html_parsing.try_get_icon_url')
    def test_extract_icon_url(self, get_icon_patch):
        def return_first_val(*a, **kwargs):
            return a[0]
        get_icon_patch.side_effect = return_first_val
        self.assertEqual('http://www.pariszigzag.fr/wp-content/themes'
                         '/paris_zigzag_2016/favicon.ico',
                         extract_icon_url(self.article))
        self.assertEqual('https://s.ytimg.com/yts/img/favicon-vflz7uhzw.ico',
                         extract_icon_url(self.article2))
