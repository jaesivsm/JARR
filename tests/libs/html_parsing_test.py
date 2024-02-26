import unittest

from unittest.mock import patch
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
        resp.url = 'https://www.youtube.com/@BenzaieLive2'
        resp.encoding = 'utf8'
        with open('tests/fixtures/article-2.html', 'rb') as fd:
            setattr(resp, '_content', fd.read())
        return resp

    def test_extract_title(self):
        self.assertEqual('Les plus belles boulangeries de Paris',
                         extract_title(self.article))
        self.assertEqual("BenzaieLive", extract_title(self.article2))

    def test_extract_feed_links(self):
        self.assertEqual(self.article.url + '/feed',
                         list(extract_feed_links(self.article))[0])
        yt_feed_link = ('https://www.youtube.com/feeds/videos.xml'
                        '?channel_id=UCOWsWZTiXkbvQvtWO9RA0gA')
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
        self.assertEqual(
            'https://www.youtube.com/s/desktop/d8e1215c/img/favicon.ico',
            extract_icon_url(self.article2))
