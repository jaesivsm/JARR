from random import randint
from datetime import timedelta
from tests.base import BaseJarrTest
from tests.utils import update_on_all_objs

from jarr.lib.reasons import ClusterReason
from jarr.controllers import (ClusterController, ArticleController,
                              FeedController, CategoryController,
                              UserController)


class ClusterControllerTest(BaseJarrTest):

    def assertNotInCluster(self, article, cluster):
        self.assertNotEqual(article.cluster_id, cluster.id,
                "article %r cluster %r is %r" % (
                    article, article.cluster, cluster))

    def assertInCluster(self, article, cluster, reason=ClusterReason.link):
        self.assertEqual(article.cluster_id, cluster.id,
                "article %d:%r:%r cluster %d is not %d(main %d:%r)" % (
                    article.id, article.entry_id, article.link,
                    article.cluster.id, cluster.id, cluster.main_article_id,
                    cluster.main_link))
        self.assertEqual(reason, article.cluster_reason)

    @staticmethod
    def create_article_from(cluster, feed, link=None):
        assert cluster.user_id == feed.user_id
        suffix = str(randint(0, 9999))
        acontr = ArticleController(cluster.user_id)
        article = acontr.create(feed_id=feed.id,
                entry_id=cluster.main_article.entry_id + suffix,
                link=link or cluster.main_article.link,
                title=cluster.main_article.title + suffix,
                content=cluster.main_article.content + suffix,
                date=cluster.main_article.date + timedelta(1),
                retrieved_date=cluster.main_article.retrieved_date)
        ClusterController.clusterize_pending_articles()
        return acontr.read(id=article.id).first()

    def test_cluster_disabled_on_original_category(self):
        article = ArticleController().read(category_id__ne=None).first()
        art_cat_id = article.category_id
        cat_ctrl = CategoryController(article.user_id)
        cluster = article.cluster
        category = cat_ctrl.create(name='new cat')
        feed = FeedController(cluster.user_id).create(
                title='new feed', category_id=art_cat_id)
        fno_cat = FeedController(cluster.user_id).create(title='category-less')
        update_on_all_objs(articles=cluster.articles, feeds=[feed, fno_cat],
                           categories=[category], cluster_enabled=True)
        cat_ctrl.update({'id': art_cat_id}, {'cluster_enabled': False})
        article = self.create_article_from(cluster, feed)
        self.assertNotInCluster(article, cluster)
        article = self.create_article_from(cluster, fno_cat)
        self.assertNotInCluster(article, cluster)
        cat_ctrl.update({'id': art_cat_id}, {'cluster_enabled': True})
        article = self.create_article_from(cluster, fno_cat)
        self.assertInCluster(article, cluster)
        article = self.create_article_from(cluster, feed)
        self.assertInCluster(article, cluster)

    def test_cluster_tfidf_control(self):
        article = ArticleController().read(category_id__ne=None).first()
        cluster = article.cluster

        # leaving one cluster with one article
        clu_ids = [c.id for c in ClusterController().read(id__ne=cluster.id)]
        art_ids = [a.id for a in ArticleController().read(
                id__ne=cluster.main_article_id)]
        ArticleController().update({'id__in': art_ids}, {'cluster_id': None})
        for clu_id in clu_ids:
            ClusterController().delete(clu_id)
        for art_id in art_ids:
            ArticleController().delete(art_id)
        self.assertEqual(1, ClusterController().read().count())
        self.assertEqual(1, ArticleController().read().count())

        feed1 = FeedController(cluster.user_id).create(
                title='new feed', cluster_conf={'tfidf_min_score': -1,
                                                'tfidf_min_sample_size': 1})
        update_on_all_objs(articles=cluster.articles, feeds=[feed1],
                           cluster_tfidf_enabled=True, cluster_enabled=True)
        feed2 = FeedController(cluster.user_id).create(
                cluster_enabled=True, cluster_tfidf_enabled=False,
                title='new feed', cluster_conf={'tfidf_min_score': -1,
                                                'tfidf_min_sample_size': 1})

        article = self.create_article_from(cluster, feed1,
                link=cluster.main_article.link + 'do not match link')
        self.assertInCluster(article, cluster, ClusterReason.tf_idf)
        article = self.create_article_from(cluster, feed2,
                link=cluster.main_article.link + 'do not match link either')
        self.assertNotInCluster(article, cluster)

    def test_no_cluster_same_category_on_original_category(self):
        article = ArticleController().read(category_id__ne=None).first()
        art_cat_id = article.category_id
        cat_ctrl = CategoryController(article.user_id)
        cluster = article.cluster
        feed = FeedController(cluster.user_id).create(
                title='new feed', category_id=art_cat_id)
        update_on_all_objs(articles=cluster.articles, feeds=[feed],
                           cluster_same_category=True,
                           cluster_enabled=True)
        cat_ctrl.update({'id': art_cat_id}, {'cluster_same_category': False})
        article = self.create_article_from(cluster, feed)
        self.assertNotInCluster(article, cluster)
        cat_ctrl.update({'id': art_cat_id}, {'cluster_same_category': True})
        article = self.create_article_from(cluster, feed)
        self.assertInCluster(article, cluster)

    def test_cluster_enabled(self):
        ccontr = ClusterController()
        cluster = ccontr.read().first()
        feed = FeedController(cluster.user_id).read(
                category_id__ne=None,
                id__nin=[art.feed_id for art in cluster.articles]).first()
        category = feed.category

        # clustering works when all is true
        update_on_all_objs(articles=cluster.articles, feeds=[feed],
                           cluster_enabled=True)
        article = self.create_article_from(cluster, feed)
        self.assertInCluster(article, cluster)

        # disabling on user desactivate all clustering
        UserController().update({'id': cluster.user_id},
                {'cluster_enabled': False})
        article = self.create_article_from(cluster, feed)
        self.assertNotInCluster(article, cluster)

        # disabling on article's feed prevents from clustering
        update_on_all_objs(articles=cluster.articles, feeds=[feed],
                           cluster_enabled=True)
        FeedController().update({'id': feed.id}, {'cluster_enabled': False})
        article = self.create_article_from(cluster, feed)
        self.assertNotInCluster(article, cluster)

        # disabling on feed from cluster's articles prevents from clustering
        update_on_all_objs(articles=cluster.articles, feeds=[feed],
                           cluster_enabled=True)
        FeedController().update(
                {'id__in': [a.feed_id for a in cluster.articles]},
                {'cluster_enabled': False})
        article = self.create_article_from(cluster, feed)
        self.assertNotInCluster(article, cluster)

        # disabling on article's category prevents from clustering
        CategoryController(cluster.user_id).update(
                {'id': category.id}, {'cluster_enabled': False})
        article = self.create_article_from(cluster, feed)
        self.assertNotInCluster(article, cluster)

        update_on_all_objs(articles=cluster.articles, feeds=[feed],
                           cluster_enabled=True)
        article = self.create_article_from(cluster, feed)
        self.assertInCluster(article, cluster)

    def test_cluster_same_feed(self):
        article = ArticleController().read(category_id__ne=None).first()
        cluster = article.cluster
        # all is enabled, article in cluster
        update_on_all_objs(articles=cluster.articles, cluster_enabled=True,
                           cluster_same_feed=True)
        article = self.create_article_from(cluster, cluster.main_article.feed)
        self.assertInCluster(article, cluster)
        # feed's disabled, won't cluster
        FeedController().update(
                {'id__in': [a.feed_id for a in cluster.articles]},
                {'cluster_same_feed': False})
        article = self.create_article_from(cluster, cluster.main_article.feed)
        self.assertNotInCluster(article, cluster)
        # category's disabled, won't cluster
        FeedController().update(
                {'id__in': [a.feed_id for a in cluster.articles]},
                {'cluster_same_feed': True})
        CategoryController().update({'id': cluster.main_article.category.id},
                {'cluster_same_feed': False})
        article = self.create_article_from(cluster, cluster.main_article.feed)
        self.assertNotInCluster(article, cluster)
        # user's disable, won't cluster
        CategoryController().update({'id': cluster.main_article.category.id},
                {'cluster_same_feed': True})
        UserController().update({'id': cluster.user_id},
                {'cluster_same_feed': False})
        article = self.create_article_from(cluster, cluster.main_article.feed)
        self.assertNotInCluster(article, cluster)
        # reenabling user, will cluster
        UserController().update({'id': cluster.user_id},
                {'cluster_same_feed': True})
        article = self.create_article_from(cluster, cluster.main_article.feed)
        self.assertInCluster(article, cluster)

    def test_cluster_same_category(self):
        article = ArticleController().read(category_id__ne=None).first()
        cluster = article.cluster
        feed = FeedController(cluster.user_id).create(title='new feed',
                category_id=cluster.main_article.category_id,
                cluster_enabled=True, cluster_same_category=True)
        # all is enabled, article in cluster
        update_on_all_objs(articles=cluster.articles, feeds=[feed],
                           cluster_enabled=True, cluster_same_category=True)
        article = self.create_article_from(cluster, feed)
        self.assertInCluster(article, cluster)
        # cluster's feed is disabled, won't cluster
        FeedController().update(
                {'id__in': [a.feed_id for a in cluster.articles]},
                {'cluster_same_category': False})
        article = self.create_article_from(cluster, feed)
        self.assertNotInCluster(article, cluster)
        # new article's feed is disabled, won't cluster
        FeedController().update(
                {'id__in': [a.feed_id for a in cluster.articles]},
                {'cluster_same_category': True})
        FeedController().update({'id': feed.id},
                {'cluster_same_category': False})
        article = self.create_article_from(cluster, feed)
        self.assertNotInCluster(article, cluster)
        # category's disabled, won't cluster
        FeedController().update({'id': feed.id},
                {'cluster_same_category': True})
        CategoryController().update({'id': cluster.main_article.category.id},
                {'cluster_same_category': False})
        article = self.create_article_from(cluster, feed)
        self.assertNotInCluster(article, cluster)
        # user's disable, won't cluster
        CategoryController().update({'id': cluster.main_article.category.id},
                {'cluster_same_category': True})
        UserController().update({'id': cluster.user_id},
                {'cluster_same_category': False})
        article = self.create_article_from(cluster, feed)
        self.assertNotInCluster(article, cluster)
        # reenabling user, will cluster
        UserController().update({'id': cluster.user_id},
                {'cluster_same_category': True})
        article = self.create_article_from(cluster, feed)
        self.assertInCluster(article, cluster)
