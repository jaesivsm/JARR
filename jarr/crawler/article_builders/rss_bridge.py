from bs4 import BeautifulSoup

from jarr.crawler.article_builders.classic import ClassicArticleBuilder
from jarr.lib.enums import ArticleType


class RSSBridgeArticleBuilder(ClassicArticleBuilder):

    @property
    def do_skip_creation(self):
        title = self.entry.get('title') or ''
        if title.startswith('Bridge returned error'):
            return True
        return super().do_skip_creation


class RSSBridgeTwitterArticleBuilder(RSSBridgeArticleBuilder):

    def enhance(self):
        try:
            content = self.entry['content'][0]['value']
            content_type = self.entry['content'][0].get('type', 'text/html')
        except (KeyError, IndexError):
            return
        if content_type != 'text/html':
            return
        soup = BeautifulSoup(content, 'html.parser')
        og_link = self.article['link']
        try:  # trying to find the last link in the tweet
            last_link = soup.find_all('a')[-1]
            self.article['link'] = last_link.attrs['href']
        except (KeyError, AttributeError, TypeError, IndexError):
            self.article['link'] = og_link
        else:
            try:  # link is the image if the link contains the images
                img = last_link.find_all('img')[0]
                self.article['link'] = img.attrs['src']
                self.article['article_type'] = ArticleType.image
            except (KeyError, AttributeError, TypeError, IndexError):
                pass
        return super().enhance()
