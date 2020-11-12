import logging

from jarr.bootstrap import conf
from jarr.crawler.crawlers.classic import ClassicCrawler
from jarr.crawler.lib.headers_handling import prepare_headers
from jarr.lib.const import GOOGLE_BOT_UA
from jarr.lib.enums import FeedType
from jarr.lib.utils import jarr_get

logger = logging.getLogger(__name__)


class TumblrCrawler(ClassicCrawler):
    feed_type = FeedType.tumblr

    def request(self):
        headers = prepare_headers(self.feed)
        # using google bot header to trick tumblr rss...
        headers['User-Agent'] = GOOGLE_BOT_UA
        return jarr_get(self.get_url(),
                        timeout=conf.crawler.timeout,
                        user_agent=conf.crawler.user_agent,
                        headers=headers)
