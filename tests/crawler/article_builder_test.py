from tests.base import BaseJarrTest
from jarr.crawler.article_builders.classic import ClassicArticleBuilder
import json
from jarr.controllers import FeedController, ArticleController
from mock import Mock


class CrawlerMainTest(BaseJarrTest):

    def entry_w_enclosure(self):
        with open('tests/fixtures/entry-with-enclosure.json') as fd:
            return json.load(fd)

    def test_articles_with_enclosure(self):
        feed = FeedController().read().first()
        builder = ClassicArticleBuilder(feed, self.entry_w_enclosure)
        self.assertIsNone(builder.article.get('article_type'))
        raw_articles = list(builder.enhance())
        self.assertEqual(2, raw_articles)
        self.assertEqual('audio', raw_articles[1]['article_type'].value)
        articles = []
        for raw_article in raw_articles:
            articles.append(
                ArticleController(feed.user_id).create(**raw_article))
        ClusterController(feed.user_id).clusterize_pending_articles()
        a1 = ArticleController().get(id=articles[0].id)
        a2 = ArticleController().get(id=articles[1].id)
        self.assertEqual(a1.cluster_id, a2.cluster_id)

