import json

from jarr.controllers import (ArticleController, ClusterController,
                              FeedController, UserController)
from jarr.crawler.article_builders.classic import ClassicArticleBuilder
from mock import patch
from tests.base import BaseJarrTest


class CrawlerMainTest(BaseJarrTest):

    @property
    def entry_w_enclosure(self):
        with open('tests/fixtures/entry-with-enclosure.json') as fd:
            return json.load(fd)

    def test_articles_with_enclosure(self):
        feed = FeedController().read().first()
        UserController().update({'id': feed.user_id},
                                {'cluster_enabled': True})
        builder = ClassicArticleBuilder(feed, self.entry_w_enclosure)
        self.assertIsNone(builder.article.get('article_type'))
        raw_articles = list(builder.enhance())
        self.assertEqual(2, len(raw_articles))
        self.assertEqual('audio', raw_articles[1]['article_type'].value)
        articles = []
        for raw_article in raw_articles:
            articles.append(
                ArticleController(feed.user_id).create(**raw_article))
        ClusterController(feed.user_id).clusterize_pending_articles()
        a1 = ArticleController().get(id=articles[0].id)
        a2 = ArticleController().get(id=articles[1].id)
        self.assertEqual(a1.cluster_id, a2.cluster_id)

    @patch('jarr.lib.content_generator.TruncatedContentGenerator.generate')
    def test_articles_with_enclosure_and_fetched_content(self, truncated_cnt):
        truncated_cnt.return_value = {'type': 'fetched',
                                      'title': 'holy grail',
                                      'content': 'blue, no read, aaah',
                                      'link': 'https://monthy.python/brian'}
        feed = FeedController().read().first()
        FeedController().update({'id': feed.id}, {'truncated_content': True})
        UserController().update({'id': feed.user_id},
                                {'cluster_enabled': True})
        builder = ClassicArticleBuilder(feed, self.entry_w_enclosure)
        self.assertIsNone(builder.article.get('article_type'))
        raw_articles = list(builder.enhance())
        self.assertEqual(2, len(raw_articles))
        self.assertEqual('audio', raw_articles[1]['article_type'].value)
        articles = []
        for raw_article in raw_articles:
            articles.append(
                ArticleController(feed.user_id).create(**raw_article))
        ClusterController(feed.user_id).clusterize_pending_articles()
        a1 = ArticleController().get(id=articles[0].id)
        a2 = ArticleController().get(id=articles[1].id)
        self.assertEqual(a1.cluster_id, a2.cluster_id)
