import logging
from urllib.parse import urlencode

from jarr.utils import jarr_get
from jarr.controllers.article import ArticleController
from jarr.lib.article_cleaner import clean_urls
from jarr.bootstrap import conf
from .base import article_parsing

logger = logging.getLogger(__name__)
READABILITY_PARSER = 'https://mercury.postlight.com/parser?'


def _get_article(cluster, **kwargs):
    if kwargs.get('article_id'):
        return next(article for article in cluster.articles
                    if article.id == kwargs['article_id'])
    return cluster.main_article


@article_parsing.connect
def mercury_integration(sender, user, feed, cluster, **kwargs):
    is_mercury_forbidden = not bool(kwargs.get('mercury_may_parse'))
    is_mercury_unavailable = not bool(conf.plugins.readability_key
                                      or user.readability_key)
    parsing_auto = feed.readability_auto_parse
    parsing_triggered = bool(kwargs.get('mercury_parse'))
    if is_mercury_forbidden or is_mercury_unavailable \
            or not (parsing_auto or parsing_triggered):
        return
    article = _get_article(cluster, **kwargs)
    if article.readability_parsed:
        return

    url = READABILITY_PARSER + urlencode({'url': article.link})
    key = user.readability_key or conf.plugins.readability_key
    try:
        response = jarr_get(url,
                user_agent=conf.crawler.user_agent,
                timeout=conf.crawler.timeout,
                headers={'x-api-key': key})
        response.raise_for_status()
        json = response.json()
        if not json:
            raise Exception('Mercury responded with %r(%d)'
                            % (json, response.status_code))
        if 'content' not in json:
            raise Exception('Mercury responded without content')
    except Exception as error:
        print(error)
        return
    artc = ArticleController(user.id)
    new_content = clean_urls(json['content'].replace('&apos;', "'"),
                                article.link, fix_readability=True)

    artc.update({'id': article.id},
                {'readability_parsed': True, 'content': new_content})

    article['content'], article['readability_parsed'] = new_content, True
    return