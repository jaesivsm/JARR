import unittest
from jarr.bootstrap import feed_creation, entry_parsing

CONTENT = """<table><tr><td>
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

    def test_feed_creation(self):
        feed = {'link': 'http://www.reddit.com/r/france/.rss'}
        feed_creation.send('test', feed=feed)
        self.assertTrue(feed.get('integration_reddit'))

    def test_feed_creation_https(self):
        feed = {'link': 'https://www.reddit.com/r/france/.rss'}
        feed_creation.send('test', feed=feed)
        self.assertTrue(feed.get('integration_reddit'))

    def test_match_light_parsing_nok(self):
        feed = {'integration_reddit': True}
        tags = [{'scheme': None, 'term': 'to', 'label': ''},
                {'scheme': None, 'term': 'be', 'label': ''},
                {'scheme': None, 'term': 'removed', 'label': ''}]
        entry = {'content': [{'value': CONTENT[:-40]}], 'tags': tags}
        entry_parsing.send('test', feed=feed, entry=entry)
        self.assertTrue('link' not in entry)
        self.assertTrue('comments' not in entry)
        self.assertEqual(entry['tags'], tags)

    def test_match_light_parsing_ok(self):
        feed = {'integration_reddit': True,
                'link': 'https://www.reddit.com/r/france/.rss'}
        tags = [{'scheme': None, 'term': 'to', 'label': ''},
                {'scheme': None, 'term': 'be', 'label': ''},
                {'scheme': None, 'term': 'removed', 'label': ''}]
        entry = {'content': [{'value': CONTENT}], 'tags': tags}
        entry_parsing.send('test', feed=feed, entry=entry)
        self.assertEqual(entry['link'], 'https://supload.com/rJY-37gLe')
        self.assertEqual(entry['comments'], 'https://www.reddit.com/r/'
                'Map_Porn/comments/5mxq4o/'
                'map_of_irish_clans_in_times_of_henry_viii_1294/')
        self.assertEqual(entry['tags'], [])
