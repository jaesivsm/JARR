from random import randint
from datetime import timedelta
from mock import Mock

from tests.base import BaseJarrTest
from tests.utils import update_on_all_objs

from jarr.lib.utils import utc_now
from jarr.controllers import (ArticleController,
                              ClusterController, FeedController)


class ClusterControllerTest(BaseJarrTest):
    _contr_cls = ClusterController

    def test_delete(self):
        clu_ctrl = ClusterController()
        for cluster in clu_ctrl.read():
            clu_ctrl.delete(cluster.id)
        self.assertEqual(0, ClusterController(2).read().count())
        self.assertEqual(0, ArticleController(2).read().count())

    @staticmethod
    def _clone_article(acontr, article, feed):
        # making sure collision will happen with this article
        for art_to_del in acontr.read(link=article.link, id__ne=article.id):
            acontr.delete(art_to_del.id)
        suffix = str(randint(0, 9999))
        acontr.create(feed_id=feed.id,
                      entry_id=article.entry_id + suffix,
                      link=article.link,
                      title=article.title + suffix,
                      content=article.content + suffix,
                      date=article.date + timedelta(1),
                      retrieved_date=article.retrieved_date + timedelta(1))

    def test_article_get_unread(self):
        self.assertEqual({1: 3, 2: 3, 3: 3, 7: 3, 8: 3, 9: 3},
                ClusterController(2).count_by_feed(read=False))
        self.assertEqual({4: 3, 5: 3, 6: 3, 10: 3, 11: 3, 12: 3},
                ClusterController(3).count_by_feed(read=False))

    def test_unread_on_cluster(self):
        ccontr = ClusterController()
        fcontr = FeedController()
        cluster = ccontr.read().first()
        ccontr.update({'id': cluster.id}, {'read': True})
        feed = fcontr.read(user_id=cluster.user_id,
                    id__ne=cluster.main_article.feed_id).first()
        update_on_all_objs(feeds=[feed], cluster_enabled=True)
        #fcontr.update({'id': feed.id}, {'cluster_wake_up': True})
        self._clone_article(ArticleController(), cluster.main_article, feed)
        ClusterController.clusterize_pending_articles()
        ccontr.get(id=cluster.id)
        self.assertFalse(cluster.read)

    def test_adding_to_cluster_by_link(self):
        ccontr = ClusterController()

        cluster = ccontr.read().first()
        ccontr.update({'id': cluster.id}, {'read': True})
        cluster = ccontr.get(id=cluster.id)
        self.assertTrue(cluster.read)
        article = cluster.articles[0]
        articles_count = len(cluster.articles)

        fcontr = FeedController(cluster.user_id)
        acontr = ArticleController(cluster.user_id)
        fcontr.update({'id': article.feed_id}, {'cluster_wake_up': True})
        feed = fcontr.read(id__ne=article.feed_id).first()
        update_on_all_objs(articles=[article], feeds=[feed],
                cluster_enabled=True)

        self._clone_article(acontr, article, feed)
        ccontr.clusterize_pending_articles()

        cluster = ccontr.get(id=cluster.id)
        self.assertEqual(articles_count + 1, len(cluster.articles))
        self.assertFalse(cluster.read)

    def test_similarity_clustering(self):
        cluster_conf = {'tfidf_min_score': 0.6, 'tfidf_min_sample_size': 10}
        user = Mock(cluster_conf=cluster_conf)
        category = Mock(cluster_conf=cluster_conf)
        feed = Mock(cluster_conf=cluster_conf, user=user, category=category)
        cluster = Mock()
        def gen_articles(factor):
            return [Mock(simple_vector={'Sarkozy': 1, 'garb': 1, 'justice': 1},
                         feed=feed, cluster=cluster)] \
                 + [Mock(feed=feed,
                        simple_vector={'Sark': 1, 'garbge': 1, 'vote': 1}),
                    Mock(feed=feed,
                        simple_vector={'Sark': 1, 'garbae': 1, 'debat': 1}),
                    Mock(feed=feed,
                        simple_vector={'Sark': 1, 'garbag': 1, 'blague': 1}),
                    Mock(feed=feed,
                        simple_vector={'Sark': 1, 'garage': 1, 'chans': 1})] \
                            * factor
        ccontr = ClusterController()
        ccontr._get_query_for_clustering = Mock(return_value=gen_articles(2))

        matching_article = Mock(
                simple_vector={'Morano': 1, 'garb': 1, 'justice': 1},
                date=utc_now(), lang='fr', feed=feed)

        self.assertIsNone(ccontr._get_cluster_by_similarity(matching_article))
        ccontr._get_query_for_clustering = Mock(return_value=gen_articles(100))
        self.assertEqual(ccontr._get_cluster_by_similarity(matching_article),
                         cluster)

        solo_article = Mock(simple_vector={'Sark': 1, 'fleur': 1},
                            date=utc_now(), lang='fr', feed=feed)
        self.assertNotEqual(cluster,
                ccontr._get_cluster_by_similarity(solo_article))
        self.assertIsNone(ccontr._get_cluster_by_similarity(solo_article))

    def test_no_mixup(self):
        acontr = ArticleController()
        ccontr = ClusterController()
        total_clusters = len(list(ccontr.read()))
        total_articles = len(list(acontr.read()))
        for cluster in ccontr.read():
            self.assertEqual(1, len(cluster.articles))

        for article in acontr.read():
            acontr.create(
                    entry_id=article.entry_id,
                    feed_id=article.feed_id,
                    title=article.title,
                    content=article.content,
                    link=article.link)

        ClusterController.clusterize_pending_articles()
        self.assertEqual(2 * total_articles, len(list(acontr.read())))
        self.assertEqual(2 * total_clusters, len(list(ccontr.read())))

        for cluster in ccontr.read():
            self.assertEqual(1, len(cluster.articles))
            self.assertEqual(1, len({a.user_id for a in cluster.articles}))

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
            self.assertEqual(1, len({a.user_id for a in cluster.articles}))
