from bs4 import BeautifulSoup

from jarr.crawler.article_builders.classic import ClassicArticleBuilder


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
        og_comments = self.article.get('comments')
        try:  # trying to find the last link in the tweet
            all_links = [link for link in soup.find_all('a')
                         if not link.find_all('img')  # no image
                         # and no profil pic
                         and og_link not in link.attrs['href']]
            if all_links:
                self.article['comments'] = self.article['link']
                self.article['link'] = all_links[-1].attrs['href']
        except (KeyError, AttributeError, TypeError, IndexError):
            self.article['link'] = og_link
            self.article['comments'] = og_comments
        yield from super().enhance()
