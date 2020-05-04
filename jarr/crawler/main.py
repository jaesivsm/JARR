import logging

import urllib3

from ep_celery import celery_app
from jarr.bootstrap import conf
from jarr.controllers import ClusterController, FeedController
from jarr.lib.enums import FeedStatus

urllib3.disable_warnings()
logger = logging.getLogger(__name__)


@celery_app.task(name='crawler.process_feed')
def process_feed(feed_id):
    crawler = FeedController().get_crawler(feed_id)
    logger.warning("%r is gonna crawl %r", crawler, feed_id)
    crawler.crawl()


@celery_app.task(name='crawler.clusterizer')
def clusterizer():
    logger.warning("Gonna clusterize pending articles")
    ClusterController.clusterize_pending_articles()


@celery_app.task(name='crawler.feed_cleaner')
def feed_cleaner():
    logger.warning("Feed cleaner - start")
    root_feed_ctrl = FeedController()
    feeds = list(root_feed_ctrl.read(status=FeedStatus.to_delete))
    try:
        root_feed_ctrl.update({'id__in': [feed.id for feed in feeds]},
                              {'status': FeedStatus.deleting})
        for feed in feeds:
            logger.warning("Deleting feed %r", feed)
            FeedController(feed.user_id).delete(feed.id)
    except Exception:
        logger.exception('something went wrong when deleting feeds %r', feeds)
        root_feed_ctrl.update({'id__in': [feed.id for feed in feeds]},
                              {'status': FeedStatus.to_delete})


@celery_app.task(name='crawler.scheduler')
def scheduler():
    logger.warning("Running scheduler")
    feeds = list(FeedController().list_fetchable())

    if not feeds:
        logger.debug("No feed to fetch")
        scheduler.apply_async(countdown=conf.crawler.idle_delay)
        return
    logger.debug('%d to fetch', len(feeds))
    for feed in feeds:
        process_feed.apply_async(args=[feed.id])

    feed_cleaner.apply_async()
    clusterizer.apply_async()
    scheduler.apply_async(countdown=60)
