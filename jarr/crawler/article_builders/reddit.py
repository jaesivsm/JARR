import logging

from bs4 import BeautifulSoup

from jarr.crawler.article_builders.classic import ClassicArticleBuilder

logger = logging.getLogger(__name__)


class RedditArticleBuilder(ClassicArticleBuilder):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self._article_bs = None

    def _parse_reddit_content(self, entry):
        if not self._article_bs:
            self._article_bs = BeautifulSoup(self.extract_content(entry),
                                             'html.parser')
        link, comments = self._article_bs.find_all('a')[-2:]
        if link.text != '[link]' or comments.text != '[comments]':
            raise ValueError('wrong stuff')
        return link.attrs['href'], comments.attrs['href']

    @staticmethod
    def extract_tags(entry):
        return set()  # reddit tags are irrelevant, removing them

    def extract_link(self, entry):
        try:
            link, _ = self._parse_reddit_content(entry)
        except Exception:
            return super().extract_link(entry)
        return link

    def extract_comments(self, entry):
        try:
            _, comments = self._parse_reddit_content(entry)
        except Exception:
            return super().extract_comments(entry)
        return comments
