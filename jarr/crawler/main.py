import logging

import urllib3
from datetime import datetime

from functools import wraps
from ep_celery import celery_app
from jarr.bootstrap import conf, REDIS_CONN
from jarr.controllers import (ArticleController, ClusterController,
                              FeedController)
from jarr.lib.enums import FeedStatus
from jarr.metrics import WORKER, WORKER_BATCH

urllib3.disable_warnings()
logger = logging.getLogger(__name__)


def lock(prefix, expire=60 * 60):
    def metawrapper(func):
        @wraps(func)
        def wrapper(id_):
            start = datetime.now()
            key = 'lock-%s-%d' % (prefix, id_)
            if REDIS_CONN.setnx(key):
                REDIS_CONN.expire(key, expire)
                try:
                    return func(id_)
                except Exception:
                    raise
                finally:
                    duration = (datetime.now() - start).total_seconds()
                    WORKER.labels(method=prefix).oberve(duration)
                    REDIS_CONN.delete(key)
        return wrapper
    return metawrapper


@celery_app.task(name='crawler.process_feed')
@lock('process-feed')
def process_feed(feed_id):
    crawler = FeedController().get_crawler(feed_id)
    logger.warning("%r is gonna crawl %r", crawler, feed_id)
    crawler.crawl()


@celery_app.task(name='crawler.clusterizer')
@lock('clusterizer')
def clusterizer(user_id):
    logger.warning("Gonna clusterize pending articles")
    ClusterController(user_id).clusterize_pending_articles()


@celery_app.task(name='crawler.feed_cleaner')
@lock('feed-cleaner')
def feed_cleaner(feed_id):
    logger.warning("Feed cleaner - start")
    fctrl = FeedController()
    result = fctrl.update({'id': feed_id, 'status': FeedStatus.to_delete},
                          {'status': FeedStatus.deleting})
    if not result:
        logger.error('feed %r seems locked, not doing anything', feed_id)
        return
    try:
        logger.warning("Deleting feed %r", feed_id)
        fctrl.delete(feed_id)
    except Exception:
        logger.exception('something went wrong when deleting feeds %r',
                         feed_id)
        fctrl.update({'id': feed_id}, {'status': FeedStatus.to_delete})
        raise


@celery_app.task(name='crawler.scheduler')
def scheduler():
    logger.warning("Running scheduler")
    WORKER.labels(method='scheduler').inc()
    fctrl = FeedController()
    # browsing feeds to fetch
    feeds = list(fctrl.list_fetchable())
    WORKER_BATCH.labels(worker_type='delete').observe(len(feeds))
    logger.info('%d to enqueue', len(feeds))
    for feed in feeds:
        logger.debug("scheduling to be fetched %r", feed)
        process_feed.apply_async(args=[feed.id])
    # browsing feeds to delete
    feeds_to_delete = list(fctrl.read(status=FeedStatus.to_delete))
    logger.info('%d to delete', len(feeds_to_delete))
    WORKER_BATCH.labels(worker_type='delete').observe(len(feeds_to_delete))
    for feed in feeds_to_delete:
        logger.debug("scheduling to be delete %r", feed)
        feed_cleaner.apply_async(args=[feed.id])
    # applying clusterizer
    for user_id in ArticleController.get_user_id_with_pending_articles():
        clusterizer.apply_async(args=[user_id])
    scheduler.apply_async(countdown=conf.crawler.idle_delay)
