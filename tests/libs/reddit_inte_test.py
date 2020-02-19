import unittest
from jarr.models.feed import Feed
from jarr.lib.jarr_types import FeedType
from jarr.crawler.article_builders.reddit import RedditArticleBuilder

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

    def test_match_light_parsing_ok(self):
        feed = Feed(feed_type=FeedType.reddit,
                    link='https://www.reddit.com/r/france/.rss')
        tags = [{'scheme': None, 'term': 'to', 'label': ''},
                {'scheme': None, 'term': 'be', 'label': ''},
                {'scheme': None, 'term': 'removed', 'label': ''}]
        entry = {'content': [{'value': CONTENT}], 'tags': tags}
        builder = RedditArticleBuilder(feed, entry)
        self.assertEqual(builder.article['link'],
                         'https://supload.com/rJY-37gLe')
        self.assertEqual(builder.article['comments'],
                         'https://www.reddit.com/r/Map_Porn/comments/5mxq4o/'
                         'map_of_irish_clans_in_times_of_henry_viii_1294/')
        self.assertEqual(builder.article['tags'], set())
