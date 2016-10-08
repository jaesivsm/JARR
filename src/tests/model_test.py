from tests.base import JarrFlaskCommon
from web.controllers import ArticleController


class ModelTest(JarrFlaskCommon):

    def assertInRelation(self, obj, relation):
        self.assertTrue(obj in relation, "%r not in %r" % (obj, relation))

    def test_model_relations(self):
        article = ArticleController().read(category_id__ne=None).first()
        # article relations
        self.assertIsNotNone(article.cluster)
        self.assertIsNotNone(article.category)
        self.assertIsNotNone(article.feed)
        # feed parent relation
        self.assertEquals(article.category, article.feed.category)

        self.assertInRelation(article.cluster, article.feed.clusters)
        self.assertInRelation(article.cluster, article.category.clusters)
        self.assertInRelation(article.feed, article.cluster.feeds)
        self.assertInRelation(article.category, article.cluster.categories)

        self.assertInRelation(article.cluster.main_article,
                              article.cluster.articles)
