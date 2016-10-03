from tests.base import JarrFlaskCommon


class ConstructFeedFromTest(JarrFlaskCommon):

    @property
    def jdh_feed(self):
        return {'description': '',
                'icon_url': 'https://www.journalduhacker.net/'
                    'assets/jdh-ico-2c6c8060958bf86c28b20d0c83f1bbc5.ico',
                'link': 'https://www.journalduhacker.net/rss',
                'site_link': 'https://www.journalduhacker.net/',
                'title': 'Journal du hacker'}

    def test_url(self):
        from lib.feed_utils import construct_feed_from
        self.assertEquals(self.jdh_feed,
                construct_feed_from('https://www.journalduhacker.net/'))

    def test_url_non_https(self):
        from lib.feed_utils import construct_feed_from
        self.assertEquals(self.jdh_feed,
                construct_feed_from('http://journalduhacker.net/'))

    def test_url_rss(self):
        from lib.feed_utils import construct_feed_from
        jdh_feed = self.jdh_feed
        jdh_feed['link'] = 'http://journalduhacker.net/rss'
        self.assertEquals(jdh_feed, construct_feed_from(jdh_feed['link']))
