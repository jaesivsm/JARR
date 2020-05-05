import unittest

from jarr.controllers.feed_builder import FeedBuilderController as FBC
from jarr.lib.enums import FeedType


class ConstructFeedFromTest(unittest.TestCase):

    @property
    def jdh_feed(self):
        return {'icon_url': 'https://www.journalduhacker.net/'
                    'assets/jdh-ico-311c23d65a3a9928889718838e2626c0665d83712d'
                    '488713c9a6c2ba2c676c0e.ico',
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
        self.assertEqual(
                {'feed_type': FeedType.classic,
                 'link': 'https://lesjoiesducode.fr/feed',
                 'site_link': 'https://lesjoiesducode.fr',
                 'title': 'Les Joies du Code – Humour de développeurs '
                 ': gifs, memes, blagues'}, joi)

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

    def test_reddit_from_site(self):
        reddit = FBC('https://www.reddit.com/r/france/').construct()
        self.assertEqual({
            'feed_type': FeedType.reddit,
            'icon_url': 'https://www.redditstatic.com/desktop2x/'
                        'img/favicon/android-icon-192x192.png',
            'site_link': 'https://www.reddit.com/r/france/',
            'title': 'reddit'}, reddit)

    def test_reddit_from_feed(self):
        reddit = FBC('https://www.reddit.com/r/france/.rss').construct()
        self.assertEqual(
            {'description': 'La France et les Français.',
             'feed_type': FeedType.reddit,
             'icon_url': 'https://www.redditstatic.com/desktop2x/'
                         'img/favicon/android-icon-192x192.png',
             'link': 'https://www.reddit.com/r/france/.rss',
             'site_link': 'https://www.reddit.com/r/france/',
             'title': 'France'}, reddit)

    def test_instagram(self):
        insta = FBC('http://www.instagram.com/jaesivsm/').construct()
        self.assertEqual({
            'feed_type': FeedType.instagram, 'link': 'jaesivsm',
            'icon_url': 'https://www.instagram.com/static/'
            'images/ico/favicon.ico/36b3ee2d91ed.ico',
            'site_link': 'https://www.instagram.com/jaesivsm/',
            'title': 'François (@jaesivsm) '
                     'Instagram profile • 124 photos and videos'},
            insta)

    def test_twitter(self):
        feed = FBC('http://twitter.com/jaesivsm/').construct()
        self.assertEqual({
            'feed_type': FeedType.twitter, 'link': 'jaesivsm',
            'icon_url': 'https://abs.twimg.com/favicons/favicon.ico',
            'site_link': 'https://twitter.com/jaesivsm/',
            'title': 'François (@jaesivsm) | Twitter'}, feed)

    def test_soundcloud(self):
        soundcloud = FBC('//soundcloud.com/popotes-podcast/').construct()
        self.assertEqual({
            'feed_type': FeedType.soundcloud,
            'icon_url': 'https://a-v2.sndcdn.com/assets/'
            'images/sc-icons/favicon-2cadd14bdb.ico',
            'link': 'popotes-podcast',
            'site_link': 'https://soundcloud.com/popotes-podcast/',
            'title': 'SoundCloud'}, soundcloud)

    def test_youtube(self):
        yt_channel = 'www.youtube.com/channel/UCOWsWZTiXkbvQvtWO9RA0gA'
        youtube = FBC(yt_channel).construct()
        self.assertEqual({
            'feed_type': FeedType.classic,
            'icon_url': 'https://s.ytimg.com/yts/img/favicon-vfl8qSV2F.ico',
            'link': 'https://www.youtube.com/feeds/videos.xml'
                    '?channel_id=UCOWsWZTiXkbvQvtWO9RA0gA',
            'site_link': 'https://www.youtube.com/channel/'
                         'UCOWsWZTiXkbvQvtWO9RA0gA',
            'title': 'BenzaieLive'}, youtube)

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
