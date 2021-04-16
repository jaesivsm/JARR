from mock import Mock, patch

from jarr.controllers.article import ArticleController
from jarr.controllers.article_clusterizer import Clusterizer
from jarr.controllers.cluster import ClusterController
from jarr.controllers.feed import FeedController
from jarr.lib import content_generator
from tests.base import JarrFlaskCommon


class ContentGeneratorTest(JarrFlaskCommon):

    def setUp(self):
        super().setUp()
        self.actrl = ArticleController()
        article = self.actrl.read().first()
        ClusterController().delete(article.cluster_id, delete_articles=False)
        self.article = self.actrl.get(id=article.id)
        content_generator.get_content_generator.cache_clear()

    def set_truncated_content(self, **kwargs):
        kwargs.update({'truncated_content': True})
        FeedController().update({'id': self.article.feed.id}, kwargs)

    @patch('jarr.controllers.article.ArticleController.enhance')
    def test_article_image_enhancement(self, enhance=None):
        self.actrl.update({'id': self.article.id}, {'article_type': 'image',
                                                    'vector': None})
        self.assertEqual(content_generator.ImageContentGenerator,
                         self.article.content_generator.__class__)
        Clusterizer().main(self.article)
        self.assertEqual('image', self.article.cluster.content.get('type'))
        self.assertEqual(self.article.link,
                         self.article.cluster.content.get('src'))
        self.assertEqual(1, enhance.call_count)
        self.assertIsNone(self.article.vector)

    @patch('jarr.controllers.article.ArticleController.enhance')
    def test_article_embedded_enhancement(self, enhance=None):
        self.actrl.update({'id': self.article.id},
                          {'article_type': 'embedded',
                           'link': "https://www.youtube.com/"
                           "watch?v=scbrjaqM3Oc",
                           "vector": None})
        self.assertEqual(content_generator.EmbeddedContentGenerator,
                         self.article.content_generator.__class__)
        Clusterizer().main(self.article)
        self.assertEqual("embedded",
                         self.article.cluster.content.get('type'))
        self.assertEqual("youtube",
                         self.article.cluster.content.get('player'))
        self.assertEqual("scbrjaqM3Oc",
                         self.article.cluster.content.get('videoId'))
        self.assertEqual(1, enhance.call_count)
        self.assertIsNone(self.article.vector)

    def test_article_image_enhancement_on_truncated(self):
        self.set_truncated_content()
        self.test_article_image_enhancement()

    def test_article_embedded_enhancement_on_truncated(self):
        self.set_truncated_content()
        self.test_article_embedded_enhancement()

    @patch('jarr.lib.content_generator.Goose')
    @patch('jarr.lib.content_generator.ContentGenerator._from_goose_to_html')
    def test_article_truncated_enhancement(
            self, from_goose=None, goose=None,
            cg=content_generator.TruncatedContentGenerator):
        from_goose.return_value = 'my collated content'
        patched_goose = Mock(opengraph={'locale': 'en'},
                             meta_lang='fr',
                             final_url='my final url',
                             meta_keywords='Monthy Python, Brian',
                             tags=['The Holy Graal', 'Monthy Python'],
                             title='Flying Circus',
                             cleaned_text="Bring out your dead !")
        goose.return_value.extract.return_value = patched_goose
        self.set_truncated_content()
        self.assertEqual(cg, self.article.content_generator.__class__)
        self.article = self.actrl.get(id=self.article.id)
        Clusterizer().main(self.article)
        self.assertEqual(3, len(self.article.tags))
        self.assertEqual('en', self.article.lang)
        self.assertEqual('Flying Circus', self.article.title)
        self.assertEqual('Flying Circus', self.article.cluster.main_title)
        self.assertEqual({'brian': 1, 'bring': 1, 'circus': 1, 'dead': 1,
                          'fli': 1, 'graal': 1, 'holi': 1, 'monthi': 1,
                          'python': 1}, self.article.simple_vector)

    @patch('jarr.lib.content_generator.Goose')
    @patch('jarr.lib.content_generator.ContentGenerator._from_goose_to_html')
    def test_reddit_original_enhancement(self, from_goose, goose):
        self.set_truncated_content(feed_type='reddit')
        self.actrl.update({'id': self.article.id},
                          {'comments': self.article.link})
        self.assertEqual(content_generator.RedditContentGenerator,
                         self.article.content_generator.__class__)
        Clusterizer().main(self.article)
        self.assertEqual(0, from_goose.call_count)
        self.assertEqual(0, goose.call_count)
        self.assertEqual({}, self.article.cluster.content)

    @patch('jarr.lib.content_generator.Goose')
    @patch('jarr.lib.content_generator.ContentGenerator._from_goose_to_html')
    def test_reddit_image_link_enhancement(self, from_goose, goose):
        self.set_truncated_content(feed_type='reddit')
        self.actrl.update({'id': self.article.id}, {'article_type': 'image'})
        self.test_article_image_enhancement()
        self.assertEqual(content_generator.ImageContentGenerator,
                         self.article.content_generator.__class__)
        self.assertEqual(0, from_goose.call_count)
        self.assertEqual(0, goose.call_count)

    def test_reddit_truncated_enhancement(self):
        self.set_truncated_content(feed_type='reddit')
        self.test_article_truncated_enhancement(
                cg=content_generator.RedditContentGenerator)
