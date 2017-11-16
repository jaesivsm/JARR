import unittest
import urllib

from mock import patch
from requests import Response

from lib.html_parsing import (extract_title, extract_tags, extract_icon_url,
                              extract_feed_link, extract_lang)


class HTMLParsingTest(unittest.TestCase):

    @property
    def article(self):
        resp = Response()
        resp.url = 'http://www.pariszigzag.fr/paris-insolite-secret/'\
                   'les-plus-belles-boulangeries-de-paris'
        resp.encoding = 'utf8'
        with open('src/tests/fixtures/article.html', 'rb') as fd:
            resp._content = fd.read()
        return resp

    @property
    def article2(self):
        resp = Response()
        resp.url = 'https://www.youtube.com/watch?v=scbrjaqM3Oc'
        resp.encoding = 'utf8'
        with open('src/tests/fixtures/article-2.html', 'rb') as fd:
            resp._content = fd.read()
        return resp

    def test_extract_tags(self):
        self.assertEqual(set(), extract_tags(self.article))
        self.assertEqual({'twitch', 'games'}, extract_tags(self.article2))

    def test_extract_title(self):
        self.assertEqual('Les plus belles boulangeries de Paris',
                          extract_title(self.article))
        self.assertEqual("Ceci n'est pas Old Boy - Owlboy (suite) "
                          "- Benzaie Live", extract_title(self.article2))

    def test_extract_lang(self):
        self.assertEqual('fr_FR', extract_lang(self.article))
        self.assertEqual('fr', extract_lang(self.article2))

    def test_extract_feed_link(self):
        feed_split = urllib.parse.urlsplit(self.article.url)
        self.assertEqual(self.article.url + '/feed',
                          extract_feed_link(self.article, feed_split))

        yt_feed_link = 'http://www.youtube.com/oembed?url=https%3A%2F%2F'\
                       'www.youtube.com%2Fwatch%3Fv%3DscbrjaqM3Oc&format=xml'
        feed_split = urllib.parse.urlsplit(self.article2.url)
        self.assertEqual(yt_feed_link,
                          extract_feed_link(self.article2, feed_split))

    @patch('lib.html_parsing.try_get_icon_url')
    def test_extract_icon_url(self, get_icon_patch):
        def return_first_val(*a, **kwargs):
            return a[0]
        get_icon_patch.side_effect = return_first_val
        split = urllib.parse.urlsplit(self.article.url)
        self.assertEqual('http://www.pariszigzag.fr/wp-content/themes'
                          '/paris_zigzag_2016/favicon.ico',
                          extract_icon_url(self.article, split, split))
        split = urllib.parse.urlsplit(self.article2.url)
        self.assertEqual('https://s.ytimg.com/yts/img/favicon-vflz7uhzw.ico',
                          extract_icon_url(self.article2, split, split))
