import unittest

from lib.feed_utils import construct_feed_from


class ConstructFeedFromTest(unittest.TestCase):

    @property
    def jdh_feed(self):
        return {'icon_url': 'https://www.journalduhacker.net/'
                    'assets/jdh-ico-2c6c8060958bf86c28b20d0c83f1bbc5.ico',
                'link': 'https://www.journalduhacker.net/rss',
                'site_link': 'https://www.journalduhacker.net/',
                'title': 'Journal du hacker'}

    def test_url(self):
        self.assertEquals(self.jdh_feed,
                construct_feed_from('https://www.journalduhacker.net/'))

    def test_url_non_https(self):
        self.assertEquals(self.jdh_feed,
                construct_feed_from('http://journalduhacker.net/'))

    def test_url_rss(self):
        jdh_feed = self.jdh_feed
        jdh_feed['link'] = 'http://journalduhacker.net/rss'
        self.assertEquals(jdh_feed, construct_feed_from(jdh_feed['link']))

    def test_joies_du_code(self):
        self.assertEquals(
                {'description':
                    "Les joies du code, l'instant GIF des développeurs !",
                 'icon_url': 'http://ljdchost.com/ljdc-theme/favicons/favicon.ico?v=9BK2m20LWn',
                 'link': 'http://lesjoiesducode.tumblr.com/rss',
                 'site_link': 'http://lesjoiesducode.fr/',
                 'title': 'Les joies du code'},
                construct_feed_from('http://lesjoiesducode.tumblr.com/rss'))

    def test_apod(self):
        self.assertEquals(
                {'icon_url': 'http://apod.nasa.gov/favicon.ico',
                 'link': None,
                 'site_link': 'http://apod.nasa.gov/',
                 'title': 'Astronomy Picture of the Day'},
                construct_feed_from('http://apod.nasa.gov/'))
        self.assertEquals(
                {'description': 'Astronomy Picture of the Day',
                 'icon_url': 'http://apod.nasa.gov/favicon.ico',
                 'link': 'http://apod.nasa.gov/apod.rss',
                 'site_link': 'http://antwrp.gsfc.nasa.gov/',
                 'title': 'APOD'},
                construct_feed_from('http://apod.nasa.gov/apod.rss'))
