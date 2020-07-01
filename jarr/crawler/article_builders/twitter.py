from jarr.crawler.article_builders.classic import ClassicArticleBuilder


class TwitterArticleBuilder(ClassicArticleBuilder):

    def __init__(self, feed, entry):
        super().__init__(feed, entry)
        self._title = None
        self._link = None
        self._parse_rss_bridge_twitter_entry()

    def _parse_rss_bridge_twitter_entry():
        try:
            for token in self.entry['title'].split()[::-1]:
                if not token.startswith('https://t.co/'):
                    continue  # token is not a shortened url
                head = self._head(token)
                if head.url.startswith('https://twitter'):
                    continue  # url is twitter internal
                self._link = head.url
                token_position = entry['title'].find(token)
                self._title = entry['title'][:token_position].strip()
        except (AttributeError, IndexError, ValueError):
            self._title = self._link = None

    def extract_link(self, entry):
        if self._link:
            return self._link
        return entry.get('link')

    def extract_title(self, entry):
        if self._title:
            return self._title
        return entry.get('title')

    @staticmethod
    def extract_comments(entry):
        return entry.get('link')
