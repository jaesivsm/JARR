import unittest

from jarr_common.feed_utils import construct_feed_from
from jarr.bootstrap import conf

cff_kw = {'timeout': conf.crawler.timeout,
          'user_agent': conf.crawler.user_agent}


class ConstructFeedFromTest(unittest.TestCase):

    @property
    def jdh_feed(self):
        return {'icon_url': 'https://www.journalduhacker.net/'
                    'assets/jdh-ico-311c23d65a3a9928889718838e2626c0665d83712d'
                    '488713c9a6c2ba2c676c0e.ico',
                'link': 'https://www.journalduhacker.net/rss',
                'site_link': 'https://www.journalduhacker.net/',
                'title': 'Journal du hacker'}

    def test_url(self):
        jh = construct_feed_from('https://www.journalduhacker.net/', **cff_kw)
        self.assertEqual(self.jdh_feed, jh)

    def test_url_non_https(self):
        jh = construct_feed_from('http://journalduhacker.net/', **cff_kw)
        self.assertEqual(self.jdh_feed, jh)

    def test_url_rss(self):
        jdh_feed = self.jdh_feed
        jdh_feed['link'] = 'http://journalduhacker.net/rss'
        jh = construct_feed_from(jdh_feed['link'], **cff_kw)
        self.assertEqual(jdh_feed, jh)

    def test_joies_du_code(self):
        joi = construct_feed_from(
                'http://lesjoiesducode.tumblr.com/rss', **cff_kw)
        self.assertEqual(
                {'description': "L'instant GIF des développeurs",
                 'icon_url': 'https://ljdchost.com/theme/favicons/favicon.ico',
                 'link': 'http://lesjoiesducode.tumblr.com/rss',
                 'site_link': 'https://lesjoiesducode.tumblr.com/',
                 'title': 'Les joies du code'}, joi)

    def test_apod(self):
        nasa = construct_feed_from('http://apod.nasa.gov/', **cff_kw)
        self.assertEqual(
                {'icon_url': 'https://apod.nasa.gov/favicon.ico',
                 'site_link': 'http://apod.nasa.gov/',
                 'title': 'Astronomy Picture of the Day'}, nasa)
        nasa = construct_feed_from('http://apod.nasa.gov/apod.rss', **cff_kw)
        self.assertEqual(
                {'description': 'Astronomy Picture of the Day',
                 'icon_url': 'https://apod.nasa.gov/favicon.ico',
                 'link': 'http://apod.nasa.gov/apod.rss',
                 'site_link': 'https://apod.nasa.gov/',
                 'title': 'APOD'}, nasa)
