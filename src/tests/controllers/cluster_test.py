from datetime import timedelta
from random import randint

from tests.base import BaseJarrTest
from web.controllers import (ArticleController, CategoryController,
                             ClusterController, FeedController)


class ClusterControllerTest(BaseJarrTest):
    _contr_cls = ClusterController

    def test_delete(self):
        clu_ctrl = ClusterController()
        for cluster in clu_ctrl.read():
            clu_ctrl.delete(cluster.id)
        self.assertEquals(0, ClusterController(2).read().count())
        self.assertEquals(0, ArticleController(2).read().count())

    def test_article_get_unread(self):
        self.assertEquals({1: 3, 2: 3, 3: 3, 7: 3, 8: 3, 9: 3},
                ClusterController(2).count_by_feed(read=False))
        self.assertEquals({4: 3, 5: 3, 6: 3, 10: 3, 11: 3, 12: 3},
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
        self.assertEquals(articles_count + 1, len(cluster.articles))
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
        self.assertEquals(articles_count, len(cluster.articles))

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
        self.assertEquals(articles_count + 1, len(cluster.articles))

    def test_no_mixup(self):
        acontr = ArticleController()
        ccontr = ClusterController()
        total_clusters = len(list(ccontr.read()))
        total_articles = len(list(acontr.read()))
        for cluster in ccontr.read():
            self.assertEquals(2, len(cluster.articles))

        for article in acontr.read():
            acontr.create(
                    entry_id=article.entry_id,
                    feed_id=article.feed_id,
                    title=article.title,
                    content=article.content,
                    link=article.link)

        self.assertEquals(2 * total_articles, len(list(acontr.read())))
        self.assertEquals(total_clusters, len(list(ccontr.read())))

        for cluster in ccontr.read():
            self.assertEquals(4, len(cluster.articles))
            self.assertEquals(1,
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
            self.assertEquals(1,
                    len(set([a.user_id for a in cluster.articles])))
