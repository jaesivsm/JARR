from random import randint
from datetime import timedelta
from mock import patch, Mock

from tests.base import BaseJarrTest

from jarr_common.utils import utc_now
from jarr.controllers import (ArticleController, CategoryController,
                              ClusterController, FeedController)


class ClusterControllerTest(BaseJarrTest):
    _contr_cls = ClusterController

    def test_delete(self):
        clu_ctrl = ClusterController()
        for cluster in clu_ctrl.read():
            clu_ctrl.delete(cluster.id)
        self.assertEqual(0, ClusterController(2).read().count())
        self.assertEqual(0, ArticleController(2).read().count())

    def test_article_get_unread(self):
        self.assertEqual({1: 3, 2: 3, 3: 3, 7: 3, 8: 3, 9: 3},
                ClusterController(2).count_by_feed(read=False))
        self.assertEqual({4: 3, 5: 3, 6: 3, 10: 3, 11: 3, 12: 3},
                ClusterController(3).count_by_feed(read=False))

    def test_adding_to_cluster_by_link(self):
        acontr = ArticleController()
        ccontr = ClusterController()
        cluster = ccontr.get(id=6)
        ccontr.update({'id': 6}, {'read': True})
        article = cluster.articles[0]
        articles_count = len(cluster.articles)
        feed = FeedController(cluster.user_id).read(
                user_id=article.user_id,
                id__ne=article.feed_id).first()
        suffix = str(randint(0, 9999))
        acontr.create(
                user_id=article.user_id,
                feed_id=feed.id,
                entry_id=article.entry_id + suffix,
                link=article.link,
                title=article.title + suffix,
                content=article.content + suffix,
                date=article.date + timedelta(1),
                retrieved_date=article.retrieved_date + timedelta(1),
        )
        cluster = ccontr.get(id=6)
        self.assertEqual(articles_count + 1, len(cluster.articles))
        self.assertTrue(cluster.read)

    def test_adding_to_cluster_by_title(self):
        article = ArticleController().get(category_id=1)
        acontr = ArticleController(article.user_id)
        ccontr = ClusterController(article.user_id)
        cluster = article.cluster
        articles_count = len(cluster.articles)
        suffix = str(randint(0, 9999))
        feed = FeedController(article.user_id).create(link=suffix,
                user_id=article.user_id, category_id=article.category_id,
                title=suffix)

        # testing with non activated category
        acontr.create(
                user_id=article.user_id,
                feed_id=feed.id,
                entry_id=article.entry_id + suffix,
                link=article.link + suffix,
                title=article.title,
                content=article.content + suffix,
                date=article.date,
                retrieved_date=article.retrieved_date,
        )
        cluster = ccontr.get(id=cluster.id)
        self.assertEqual(articles_count, len(cluster.articles))

        # testing with activated category
        CategoryController().update({'id': article.category_id},
                {'cluster_on_title': True})
        acontr.create(
                user_id=article.user_id,
                feed_id=feed.id,
                category_id=article.category_id,
                entry_id=article.entry_id + suffix,
                link=article.link + suffix + suffix,
                title=article.title,
                content=article.content + suffix,
                date=article.date,
                retrieved_date=article.retrieved_date,
        )
        cluster = ccontr.get(id=cluster.id)
        self.assertEqual(articles_count + 1, len(cluster.articles))

    @patch('jarr.controllers.cluster.ArticleController')
    def test_similarity_clustering(self, acontr_cls):
        cluster = Mock()
        def gen_articles(factor):
            return [Mock(valuable_tokens=['Sarkozy', 'garb', 'justice'],
                         cluster=cluster)] \
                 + [Mock(valuable_tokens=['Sarkozy', 'garbge', 'vote']),
                    Mock(valuable_tokens=['Sarkozy', 'garbae', 'debat']),
                    Mock(valuable_tokens=['Sarkozy', 'garbag', 'blague']),
                    Mock(valuable_tokens=['Sarkozy', 'garage', 'chanson'])] \
                            * factor
        ccontr = ClusterController()
        ccontr.tfidf_min_score = 0.6

        acontr_cls.return_value.read.return_value = gen_articles(2)

        matching_article = Mock(valuable_tokens=['Morano', 'garb', 'justice'],
                                date=utc_now(), lang='fr')

        self.assertIsNone(ccontr._get_cluster_by_similarity(matching_article))
        acontr_cls.return_value.read.return_value = gen_articles(100)
        self.assertEqual(ccontr._get_cluster_by_similarity(matching_article),
                         cluster)

        solo_article = Mock(valuable_tokens=['Sarkozy', 'fleur'],
                            date=utc_now(), lang='fr')
        self.assertNotEqual(cluster,
                ccontr._get_cluster_by_similarity(solo_article))
        self.assertIsNone(ccontr._get_cluster_by_similarity(solo_article))

    def test_no_mixup(self):
        acontr = ArticleController()
        ccontr = ClusterController()
        total_clusters = len(list(ccontr.read()))
        total_articles = len(list(acontr.read()))
        for cluster in ccontr.read():
            self.assertEqual(2, len(cluster.articles))

        for article in acontr.read():
            acontr.create(
                    entry_id=article.entry_id,
                    feed_id=article.feed_id,
                    title=article.title,
                    content=article.content,
                    link=article.link)

        self.assertEqual(2 * total_articles, len(list(acontr.read())))
        self.assertEqual(total_clusters, len(list(ccontr.read())))

        for cluster in ccontr.read():
            self.assertEqual(4, len(cluster.articles))
            self.assertEqual(1,
                    len(set([a.user_id for a in cluster.articles])))

        main_article = acontr.read().first()
        for article in acontr.read():
            acontr.create(
                    user_id=main_article.user_id,
                    feed_id=main_article.feed_id,
                    entry_id=article.entry_id,
                    title=article.title,
                    content=article.content,
                    link=article.link)

        for cluster in ccontr.read():
            self.assertEqual(1,
                    len(set([a.user_id for a in cluster.articles])))
