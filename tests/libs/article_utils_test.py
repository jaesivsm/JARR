import unittest

from mock import patch

from jarr.lib.url_cleaners import clean_urls

SAMPLE = """<a href="link_to_correct.html">
<img src="http://is_ok.com/image"/>
</a>
<a href="http://is_also_ok.fr/link">test</a>
<iframe src="http://youtube.com/an_unsecure_video">
</iframe>
<img src="http://abs.ol/ute/buggy.img%2C%20otherbuggy.img" srcset="garbage"/>
<img src="relative.img" />"""


class ArticleCleanerTest(unittest.TestCase):

    def setUp(self):
        self.sample = SAMPLE.split('\n')
        self.url = 'https://test.te'

    @patch('jarr.lib.url_cleaners.is_secure_served')
    def test_clean_clear(self, is_secure_served):
        is_secure_served.return_value = False
        result = clean_urls(SAMPLE, self.url).split('\n')
        self.assertEqual('<a href="https://test.te/link_to_correct.html">',
                         result[0])
        self.assertEqual(self.sample[1], result[1])  # unchanged
        self.assertEqual(self.sample[2], result[2])  # unchanged
        self.assertEqual(self.sample[3], result[3])  # unchanged
        self.assertEqual(self.sample[4], result[4])  # unchanged
        self.assertEqual(self.sample[6], result[6])  # unchanged
        self.assertEqual('<img src="%s/relative.img"/>' % self.url, result[7])

    @patch('jarr.lib.url_cleaners.is_secure_served')
    def test_clean_https(self, is_secure_served):
        is_secure_served.return_value = True
        result = clean_urls(SAMPLE, self.url).split('\n')
        self.assertEqual('<a href="https://test.te/link_to_correct.html">',
                         result[0])
        self.assertEqual(self.sample[1], result[1])  # unchanged
        self.assertEqual(self.sample[2], result[2])  # unchanged
        self.assertEqual(self.sample[3], result[3])  # unchanged
        self.assertEqual(
                '<iframe src="https://youtube.com/an_unsecure_video">',
                result[4])
        self.assertEqual(
                '<img src="http://abs.ol/ute/buggy.img%2C%20otherbuggy.img"/>',
                result[6])
        self.assertEqual('<img src="%s/relative.img"/>' % self.url, result[7])
