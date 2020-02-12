import logging

from bs4 import BeautifulSoup

from jarr.crawler.article_builders.classic import ClassicArticleBuilder

logger = logging.getLogger(__name__)


class KoreusArticleBuilder(ClassicArticleBuilder):

    @staticmethod
    def extract_link(entry):
        summary_detail = BeautifulSoup(entry['summary_detail']['value'],
                                       'html.parser')
        link = summary_detail.find_all('a')[0]
        return link.attrs['href']

    @staticmethod
    def extract_comments(entry):
        return entry.get('link')
