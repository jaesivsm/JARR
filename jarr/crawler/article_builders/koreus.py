import logging

from bs4 import BeautifulSoup

from jarr.crawler.article_builders.classic import ClassicArticleBuilder

logger = logging.getLogger(__name__)


class KoreusArticleBuilder(ClassicArticleBuilder):

    @staticmethod
    def extract_link(entry):
        text = None
        if entry.get('summary_detail') \
                and entry['summary_detail'].get('value'):
            text = entry['summary_detail']['value']
        elif entry.get('summary'):
            text = entry['summary']
        else:
            for content in entry.get('content') or []:
                if content and content.get('value'):
                    text = content['value']
        if text is None:
            return super().extract_link(entry)
        summary_detail = BeautifulSoup(text, 'html.parser')
        link = summary_detail.find_all('a')[0]
        return link.attrs['href']

    @staticmethod
    def extract_comments(entry):
        return entry.get('link')
