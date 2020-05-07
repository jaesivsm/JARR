import logging

import urllib3

from ep_celery import celery_app
from jarr.bootstrap import conf
from jarr.models import Article
from jarr.controllers import ArticleController, ClusterController, FeedController
from jarr.lib.enums import FeedStatus
from jarr.metrics import WORKER, WORKER_BATCH

urllib3.disable_warnings()
logger = logging.getLogger(__name__)


@celery_app.task(name='crawler.process_feed')
def process_feed(feed_id):
    WORKER.labels(method='process-feed').inc()
    crawler = FeedController().get_crawler(feed_id)
    logger.warning("%r is gonna crawl %r", crawler, feed_id)
    crawler.crawl()


@celery_app.task(name='crawler.clusterizer')
def clusterizer(user_id):
    logger.warning("Gonna clusterize pending articles")
    WORKER.labels(method='clusterizer').inc()
    ClusterController(user_id).clusterize_pending_articles()


@celery_app.task(name='crawler.feed_cleaner')
def feed_cleaner(feed_id):
    logger.warning("Feed cleaner - start")
    WORKER.labels(method='feed-cleaner').inc()
    fctrl = FeedController()
    result = fctrl.update({'id': feed_id, 'status': FeedStatus.to_delete},
                          {'status': FeedStatus.deleting})
    if not result:
        logger.error('feed %r seems locked, not doing anything', feed_id)
        return
    try:
        logger.warning("Deleting feed %r", feed)
        fctrl.delete(feed_id)
    except Exception:
        logger.exception('something went wrong when deleting feeds %r', feeds)
        root_feed_ctrl.update({'id': feed_id},
                              {'status': FeedStatus.to_delete})
        raise


@celery_app.task(name='crawler.scheduler')
def scheduler():
    logger.warning("Running scheduler")
    WORKER.labels(method='scheduler').inc()
    fctrl = FeedController()
    # browsing feeds to fetch
    feeds = list(fctrl.list_fetchable())
    WORKER_BATCH.labels(worker_batch='delete').observe(len(feeds))
    logger.info('%d to enqueue', len(feeds))
    for feed in feeds:
        logger.debug("scheduling to be fetched %r", feed)
        process_feed.apply_async(args=[feed.id])
    # browsing feeds to delete
    feeds_to_delete = list(fctrl.read(status=FeedStatus.to_delete))
    logger.info('%d to delete', len(feeds_to_delete))
    WORKER_BATCH.labels(worker_batch='delete').observe(len(feeds_to_delete))
    for feed in feeds_to_delete:
        logger.debug("scheduling to be delete %r", feed)
        feed_cleaner.apply_async(args=[feed.id])
    # applying clusterizer
    for user_id in ArticleController.get_user_id_with_pending_articles():
        clusterizer.apply_async(args=[user_id])
    scheduler.apply_async(countdown=conf.crawler.idle_delay)
