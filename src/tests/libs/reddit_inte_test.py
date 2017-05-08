import unittest

from mock import patch, Mock

from bootstrap import conf
from lib.integrations.reddit import RedditIntegration
from lib.integrations import dispatch

content = """<table><tr><td>
<a href="https://www.reddit.com/r/Map_Porn/comments/5mxq4o/\
map_of_irish_clans_in_times_of_henry_viii_1294/">
<img alt="Map of Irish clans in times of Henry VIII [1294 × 1536]"
     src="https://b.thumbs.redditmedia.com/v9V4aD-m3-rXVCv32dUmC-\
VvMzqaYvD1V0jqmYrslDo.jpg"
     title="Map of Irish clans in times of Henry VIII [1294 × 1536]"/> </a>
</td><td>   submitted by
<a href="https://www.reddit.com/user/hablador"> /u/hablador </a> <br/>
<span><a href="https://supload.com/rJY-37gLe">[link]</a></span>
<span><a href="https://www.reddit.com/r/Map_Porn/comments/5mxq4o/\
map_of_irish_clans_in_times_of_henry_viii_1294/">[comments]</a></span>
</td></tr></table>"""

class RedditIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.inte = RedditIntegration()

    def test_feed_creation(self):
        feed = {'link': 'http://www.reddit.com/r/france/.rss'}
        self.assertTrue(dispatch('feed_creation', feed))
        self.assertTrue(feed.get('integration_reddit'))

    def test_feed_creation_https(self):
        feed = {'link': 'https://www.reddit.com/r/france/.rss'}
        self.assertTrue(dispatch('feed_creation', feed))
        self.assertTrue(feed.get('integration_reddit'))

    def test_match_entry_parsiong(self):
        self.assertFalse(self.inte.match_entry_parsing({}, {}))
        self.assertFalse(self.inte.match_entry_parsing(
                {'integration_reddit': False}, {}))
        self.assertTrue(self.inte.match_entry_parsing(
                        {'integration_reddit': True,
                         'link': 'https://www.reddit.com/r/france/.rss'},
                        {'content': [{'value': 'stuff'}]}))

    def test_match_light_parsing_nok(self):
        feed = {'integration_reddit': True}
        tags = [{'scheme': None, 'term': 'to', 'label': ''},
                {'scheme': None, 'term': 'be', 'label': ''},
                {'scheme': None, 'term': 'removed', 'label': ''}]
        entry = {'content': [{'value': content[:-40]}], 'tags': tags}
        self.assertFalse(dispatch('entry_parsing', feed, entry))
        self.assertTrue('link' not in entry)
        self.assertTrue('comments' not in entry)
        self.assertEqual(entry['tags'], tags)

    def test_match_light_parsing_ok(self):
        feed = {'integration_reddit': True,
                'link': 'https://www.reddit.com/r/france/.rss'}
        tags = [{'scheme': None, 'term': 'to', 'label': ''},
                {'scheme': None, 'term': 'be', 'label': ''},
                {'scheme': None, 'term': 'removed', 'label': ''}]
        entry = {'content': [{'value': content}], 'tags': tags}
        self.assertTrue(dispatch('entry_parsing', feed, entry))
        self.assertEqual(entry['link'], 'https://supload.com/rJY-37gLe')
        self.assertEqual(entry['comments'], 'https://www.reddit.com/r/'
                'Map_Porn/comments/5mxq4o/'
                'map_of_irish_clans_in_times_of_henry_viii_1294/')
        self.assertEqual(entry['tags'], [])
