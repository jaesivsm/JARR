import unittest

from jarr.controllers.feed_builder import FeedBuilderController as FBC
from jarr.lib.enums import FeedType


class ConstructFeedFromTest(unittest.TestCase):

    @property
    def jdh_feed(self):
        return {'icon_url': 'https://www.journalduhacker.net/assets/jdh-ico-31'
                            '1c23d65a3a9928889718838e2626c0665d83712d488713c9a'
                            '6c2ba2c676c0e.ico',
                'link': 'https://www.journalduhacker.net/rss',
                'links': ['https://www.journalduhacker.net/rss',
                          'https://www.journalduhacker.net/comments.rss'],
                'site_link': 'https://www.journalduhacker.net/',
                'title': 'Journal du hacker',
                'feed_type': FeedType.classic}

    def test_url(self):
        jh = FBC('https://www.journalduhacker.net/').construct()
        self.assertEqual(self.jdh_feed, jh)

    def test_url_non_https(self):
        jh = FBC('http://journalduhacker.net/').construct()
        self.assertEqual(self.jdh_feed, jh)

    def test_url_rss(self):
        jdh_feed = self.jdh_feed
        jh = FBC('http://journalduhacker.net/rss').construct()
        self.assertEqual(jdh_feed, jh)

    def test_joies_du_code(self):
        self.maxDiff = None
        joi = FBC('https://lesjoiesducode.fr/feed').construct()
        joi.pop('icon_url')
        self.assertEqual(joi['feed_type'], FeedType.classic)
        self.assertEqual(joi['link'], 'https://lesjoiesducode.fr/feed')
        self.assertTrue('https://lesjoiesducode.fr' in joi['site_link'])
        self.assertTrue('les joies du code' in joi['title'].lower())

    def test_apod_from_site(self):
        nasa = FBC('http://apod.nasa.gov/').construct()
        self.assertEqual(
                {'icon_url': 'https://apod.nasa.gov/favicon.ico',
                 'feed_type': FeedType.classic,
                 'site_link': 'https://apod.nasa.gov/apod/astropix.html',
                 'title': 'Astronomy Picture of the Day'}, nasa)

    def test_apod_from_feed(self):
        nasa = FBC('http://apod.nasa.gov/apod.rss').construct()
        self.assertEqual(
                {'description': 'Astronomy Picture of the Day',
                 'feed_type': FeedType.classic,
                 'icon_url': 'https://apod.nasa.gov/favicon.ico',
                 'link': 'https://apod.nasa.gov/apod.rss',
                 'site_link': 'https://apod.nasa.gov/',
                 'title': 'APOD'}, nasa)

    def _test_reddit_from_site(self):
        reddit = FBC('https://www.reddit.com/r/france/').construct()
        expected = {'feed_type': FeedType.reddit, 'title': 'France',
                    'icon_url': 'https://www.redditstatic.com/desktop2x/'
                                'img/favicon/android-icon-192x192.png',
                    'site_link': 'https://www.reddit.com/r/france/',
                    'link': 'https://www.reddit.com/r/france/.rss'}
        self.assertEqual(expected, {k: reddit[k] for k in expected})

    def _test_reddit_from_feed(self):
        reddit = FBC('https://www.reddit.com/r/france/.rss').construct()
        expected = {'feed_type': FeedType.reddit, 'title': 'France',
                    'icon_url': 'https://www.redditstatic.com/desktop2x/'
                                'img/favicon/android-icon-192x192.png',
                    'link': 'https://www.reddit.com/r/france/.rss',
                    'site_link': 'https://www.reddit.com/r/france/'}
        self.assertEqual(expected, {k: reddit[k] for k in expected})

    def test_instagram(self):
        insta = FBC('http://www.instagram.com/jaesivsm/').construct()
        self.assertEqual('jaesivsm', insta['link'])
        self.assertEqual(FeedType.instagram, insta['feed_type'])

    def test_twitter(self):
        feed = FBC('http://twitter.com/jaesivsm/').construct()
        self.assertEqual('jaesivsm', feed['link'])
        self.assertEqual(FeedType.twitter, feed['feed_type'])

    def test_soundcloud(self):
        soundcloud = FBC('//soundcloud.com/popotes-podcast/').construct()
        self.assertEqual({
            'feed_type': FeedType.soundcloud,
            'icon_url': 'https://a-v2.sndcdn.com/assets/'
            'images/sc-icons/favicon-2cadd14bdb.ico',
            'link': 'popotes-podcast',
            'site_link': 'https://soundcloud.com/popotes-podcast',
            'title': 'SoundCloud'}, soundcloud)

    def test_youtube_channel_feed(self):
        url = ('https://www.youtube.com/feeds/videos.xml'
               '?channel_id=UCOWsWZTiXkbvQvtWO9RA0gA')
        feed = FBC(url).construct()
        self.assertEqual(FeedType.classic, feed['feed_type'])
        self.assertEqual(url, feed['link'])
        self.assertEqual('BenzaieLive', feed['title'])

    def test_youtube_playlist_feed(self):
        url = ("http://www.youtube.com/feeds/videos.xml"
               "?playlist_id=PLB049A6ACE1D68F6C")
        feed = FBC(url).construct()
        self.assertEqual(FeedType.classic, feed['feed_type'])
        self.assertEqual(url, feed['link'])
        self.assertEqual('Thomas VDB', feed['title'])

    def test_youtube_channel(self):
        yt_channel = 'www.youtube.com/channel/UCOWsWZTiXkbvQvtWO9RA0gA'
        feed = FBC(yt_channel).construct()
        self.assertEqual(FeedType.classic, feed['feed_type'])
        self.assertEqual('https://www.youtube.com/feeds/videos.xml'
                         '?channel_id=UCOWsWZTiXkbvQvtWO9RA0gA', feed['link'])
        self.assertEqual('BenzaieLive', feed['title'])

    def test_new_youtube_channel(self):
        yt_channel = 'www.youtube.com/@BenzaieLive2'
        feed = FBC(yt_channel).construct()
        self.assertEqual(FeedType.classic, feed['feed_type'])
        self.assertEqual('https://www.youtube.com/feeds/videos.xml'
                         '?channel_id=UCOWsWZTiXkbvQvtWO9RA0gA', feed['link'])
        self.assertEqual('BenzaieLive', feed['title'])

    def test_youtube_playlist(self):
        yt_plist = 'www.youtube.com/playlist?list=PLB049A6ACE1D68F6C'
        feed = FBC(yt_plist).construct()
        self.assertEqual(FeedType.classic, feed['feed_type'])
        self.assertEqual('https://www.youtube.com/feeds/videos.xml'
                         '?playlist_id=PLB049A6ACE1D68F6C', feed['link'])
        self.assertEqual('Thomas VDB', feed['title'])

    def test_youtube_playlist_from_video(self):
        ytplist = 'www.youtube.com/watch?v=uG2ReGlRV58&list=PLB049A6ACE1D68F6C'
        feed = FBC(ytplist).construct()
        self.assertEqual(FeedType.classic, feed['feed_type'])
        self.assertEqual('https://www.youtube.com/feeds/videos.xml'
                         '?playlist_id=PLB049A6ACE1D68F6C', feed['link'])
        self.assertEqual('Thomas VDB', feed['title'])

    def test_json(self):
        feed = FBC('https://daringfireball.net/feeds/json').construct()
        self.assertEqual({'feed_type': FeedType.json,
                          'icon_url': 'https://daringfireball.net/'
                                      'graphics/favicon-64.png',
                          'link': 'https://daringfireball.net/feeds/json',
                          'links': ['https://daringfireball.net/feeds/main',
                                    'https://daringfireball.net/feeds/json'],
                          'site_link': 'https://daringfireball.net/',
                          'title': 'Daring Fireball'}, feed)
