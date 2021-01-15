from datetime import timedelta
from random import randint

from jarr.controllers import ArticleController, FeedController
from jarr.controllers.article_clusterizer import Clusterizer
from jarr.controllers.cluster import ClusterController
from jarr.lib.clustering_af.grouper import get_best_match_and_score
from jarr.lib.clustering_af.postgres_casting import to_vector
from tests.base import BaseJarrTest
from tests.utils import update_on_all_objs


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
        return acontr.create(feed_id=feed.id,
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

    def _test_unread_on_cluster(self, read_reason):
        ccontr = ClusterController()
        fcontr = FeedController()
        cluster = ccontr.read().first()
        clusterizer = Clusterizer()
        self.assertFalse(clusterizer.get_config(cluster, 'cluster_enabled'))
        self.assertTrue(clusterizer.get_config(cluster, 'cluster_wake_up'))
        ccontr.update({'id': cluster.id}, {'read': True,
                                           'read_reason': read_reason})
        target_feed = fcontr.read(id__ne=cluster.main_article.feed_id,
                                  user_id=cluster.user_id).first()
        clusterizer = Clusterizer()
        self.assertFalse(clusterizer.get_config(
            target_feed, 'cluster_enabled'))
        fcontr.update({'id__in': [f.id for f in cluster.feeds]
                                 + [target_feed.id]},
                      {'cluster_wake_up': True, 'cluster_enabled': True})
        clusterizer = Clusterizer()
        self.assertTrue(clusterizer.get_config(cluster, 'cluster_enabled'))
        target_feed = fcontr.read(id__ne=cluster.main_article.feed_id,
                                  user_id=cluster.user_id).first()
        article = self._clone_article(ArticleController(),
                                      cluster.main_article, target_feed)
        clusterizer = Clusterizer()
        self.assertTrue(clusterizer.get_config(article, 'cluster_wake_up'))
        ClusterController(cluster.user_id).clusterize_pending_articles()
        self.assertEqual(2, len(article.cluster.articles))
        self.assertInCluster(article, cluster)
        return ccontr.get(id=cluster.id)

    def test_no_unread_on_cluster(self):
        self.assertTrue(self._test_unread_on_cluster('consulted').read)

    def test_unread_on_cluster(self):
        self.assertFalse(self._test_unread_on_cluster('marked').read)

    def test_adding_to_cluster_by_link(self):
        ccontr = ClusterController()

        cluster = ccontr.read().first()
        ccontr.update({'id': cluster.id}, {'read': True,
                                           'read_reason': 'marked'})
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
        words = 'Monthi Python Shrubberi Holi Graal life Brian'.split()
        words2 = 'And now for something completely different'.split()

        simple_vector = {word.lower(): i for i, word in enumerate(words, 1)}
        content = ' '.join([(w + ' ') * i for i, w in enumerate(words, 1)])
        actrl = ArticleController(2)
        actrl.update({}, {'vector': to_vector({'content': content})})
        for art in actrl.read():
            self.assertEqual(art.simple_vector, simple_vector)

        art1, art2, art3 = actrl.read().limit(3)
        match, score = get_best_match_and_score(art1, [art2])
        self.assertEqual(1, round(score, 10))
        self.assertEqual(match, art2)

        content = ' '.join([(w + ' ') * i for i, w in enumerate(words2, 1)])
        actrl.update({'id': art2.id},
                     {'vector': to_vector({'content': content})})
        art2 = actrl.get(id=art2.id)
        self.assertNotEqual(art2.simple_vector, art1.simple_vector)

        truncated_content = ' '.join([(w + ' ') * i
                                      for i, w in enumerate(words[:-2], 1)])
        actrl.update({'id__nin': [art1.id, art2.id, art3.id]},
                     {'vector': to_vector({'content': truncated_content})})
        match, score = get_best_match_and_score(art1, list(actrl.read()))
        self.assertEqual(1, round(score, 10))
        self.assertNotEqual(match, art2)
        self.assertEqual(match, art3)
        match, score = get_best_match_and_score(art1, [art2])
        self.assertEqual(0, score)
        self.assertEqual(match, art2)

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

        for user_id in ArticleController.get_user_id_with_pending_articles():
            ClusterController(user_id).clusterize_pending_articles()
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
