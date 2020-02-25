import logging

from bs4 import BeautifulSoup

from jarr.crawler.article_builders.classic import ClassicArticleBuilder

logger = logging.getLogger(__name__)


class RedditArticleBuilder(ClassicArticleBuilder):

    def __init__(self, *args, **kwargs):
        """Reddit article builder. Will swap link and comments."""
        self._article_bs = None
        super().__init__(*args, **kwargs)

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
            return self._parse_reddit_content(entry)[0]
        except Exception:
            return super().extract_link(entry)

    def extract_comments(self, entry):
        try:
            return self._parse_reddit_content(entry)[1]
        except Exception:
            return super().extract_comments(entry)
