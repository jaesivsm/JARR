import ssl
import conf
import asyncio
import logging
import feedparser
import dateutil.parser
from datetime import datetime
from sqlalchemy import or_

from bootstrap import db
from web.models import User
from web.controllers import FeedController, ArticleController
from web.lib.feed_utils import construct_feed_from, is_parsing_ok
from crawler.lib.article_utils import construct_article, extract_id, \
                                    get_article_content

logger = logging.getLogger(__name__)

sem = asyncio.Semaphore(5)

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


async def get(*args, **kwargs):
    # kwargs["connector"] = aiohttp.TCPConnector(verify_ssl=False)
    try:
        data = feedparser.parse(args[0])
        return data
    except Exception as e:
        raise e


async def parse_feed(user, feed):
    """
    Fetch a feed.
    Update the feed and return the articles.
    """
    parsed_feed = None
    up_feed = {}
    articles = []
    with (await sem):
        try:
            parsed_feed = await get(feed.link)
        except Exception as e:
            up_feed['last_error'] = str(e)
            up_feed['error_count'] = feed.error_count + 1
        finally:
            up_feed['last_retrieved'] = datetime.utcnow()
            if parsed_feed is None:
                FeedController().update({'id': feed.id}, up_feed)
                return

    if not is_parsing_ok(parsed_feed):
        up_feed['last_error'] = str(parsed_feed['bozo_exception'])
        up_feed['error_count'] = feed.error_count + 1
        FeedController().update({'id': feed.id}, up_feed)
        return
    if parsed_feed['entries'] != []:
        articles = parsed_feed['entries']

    up_feed['error_count'] = 0
    up_feed['last_error'] = ""

    # Feed informations
    construct_feed_from(feed.link, parsed_feed).update(up_feed)
    if feed.title and 'title' in up_feed:
        # do not override the title set by the user
        del up_feed['title']
    FeedController().update({'id': feed.id}, up_feed)

    return articles


async def insert_database(user, feed):

    articles = await parse_feed(user, feed)
    if None is articles:
        return []

    logger.debug('inserting articles for {}'.format(feed.title))

    logger.info("Database insertion...")
    new_articles = []
    art_contr = ArticleController(user.id)
    for article in articles:
        existing_article_req = art_contr.read(feed_id=feed.id,
                        **extract_id(article))
        exist = existing_article_req.count() != 0
        if exist:
            existing_article = existing_article_req.first()
            is_updated = False
            logger.debug("Article %r (%r) already in the database.",
                         article['title'], article['link'])
            content = get_article_content(article)
            if existing_article.title != article['title']:
                existing_article.title = article['title']
                is_updated = True
            if existing_article.content != content:
                existing_article.content = content
                existing_article.readed = False
                is_updated = True
            if is_updated:
                art_contr.update({'entry_id': existing_article.entry_id},
                                 existing_article.dump())
            continue
        article = construct_article(article, feed.dump())
        try:
            new_articles.append(art_contr.create(**article))
            logger.info("New article % (%r) added.",
                        article['title'], article['link'])
        except Exception:
            logger.exception("Error when inserting article in database:")
            continue
    return new_articles


async def init_process(user, feed):
    # Fetch the feed and insert new articles in the database
    articles = await insert_database(user, feed)
    logger.debug('inserted articles for %s', feed.title)
    return articles


def retrieve_feed(loop, user, feed_id=None):
    """
    Launch the processus.
    """
    logger.info("Starting to retrieve feeds.")

    # Get the list of feeds to fetch
    user = User.query.filter(User.email == user.email).first()
    feeds = [feed for feed in user.feeds if
             feed.error_count <= conf.FEED_ERROR_MAX and feed.enabled]
    if feed_id is not None:
        feeds = [feed for feed in feeds if feed.id == feed_id]

    if feeds == []:
        return

    # Launch the process for all the feeds
    tasks = [asyncio.ensure_future(init_process(user, feed)) for feed in feeds]

    try:
        loop.run_until_complete(asyncio.wait(tasks))
    except Exception:
        logger.exception('an error occured')

    logger.info("All articles retrieved. End of the processus.")
