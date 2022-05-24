import logging
from datetime import datetime, timedelta

import urllib3
from ep_celery import celery_app
from jarr.bootstrap import REDIS_CONN, conf
from jarr.controllers import (ArticleController, ClusterController,
                              FeedController, UserController)
from jarr.crawler.utils import Queues, lock, observe_worker_result_since
from jarr.lib.enums import FeedStatus
from jarr.lib.utils import utc_now
from jarr.metrics import ARTICLES, USER, WORKER_BATCH

urllib3.disable_warnings()
logger = logging.getLogger(__name__)
LOCK_EXPIRE = 60 * 60
JARR_FEED_DEL_KEY = 'jarr.feed-deleting'
JARR_CLUSTERIZER_KEY = 'jarr.clusterizer.%d'


@celery_app.task(name='crawler')
@lock('process-feed')
def process_feed(feed_id):
    feed = FeedController().get(id=feed_id)
    logger.warning("%r is gonna crawl", feed.crawler)
    feed.crawler.crawl()
    FeedController(feed.user_id).update_unread_count(feed.id)


@celery_app.task(name='clusterizer')
@lock('clusterizer')
def clusterizer(user_id):
    logger.warning("Gonna clusterize pending articles")
    ClusterController(user_id).clusterize_pending_articles()
    REDIS_CONN.delete(JARR_CLUSTERIZER_KEY % user_id)


@celery_app.task(name='feed_cleaner')
@lock('feed-cleaner')
def feed_cleaner(feed_id):
    logger.warning("Feed cleaner - start => %s", feed_id)
    WORKER_BATCH.labels(worker_type='delete').observe(1)
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
    finally:
        REDIS_CONN.delete(JARR_FEED_DEL_KEY)


@celery_app.task(name='metrics.users.any')
def metrics_users_any():
    logger.debug('Counting users')
    USER.labels(status='any').set(UserController().read().count())


@celery_app.task(name='metrics.users.active')
def metrics_users_active():
    logger.debug('Counting active users')
    threshold_connection = utc_now() - timedelta(days=conf.feed.stop_fetch)
    active = UserController().read(is_active=True,
                                   last_connection__ge=threshold_connection)
    USER.labels(status='active').set(active.count())


@celery_app.task(name='metrics.users.long_term')
def metrics_users_long_term():
    logger.debug('Counting long term users')
    threshold_connection = utc_now() - timedelta(days=conf.feed.stop_fetch)
    threshold_connection = utc_now() - timedelta(days=conf.feed.stop_fetch)
    threshold_created = utc_now() - timedelta(days=conf.feed.stop_fetch + 1)
    long_term = UserController().read(is_active=True,
                                      last_connection__ge=threshold_connection,
                                      date_created__lt=threshold_created)
    USER.labels(status='long_term').set(long_term.count())


@celery_app.task(name='metrics.articles.unclustered')
def metrics_articles_unclustered():
    logger.debug('Counting unclustered articles')
    unclustered = ArticleController().count_unclustered()
    ARTICLES.labels(status='unclustered').set(unclustered)


@celery_app.task(name='scheduler')
def scheduler():
    logger.warning("Running scheduler")
    start = datetime.now()
    fctrl = FeedController()
    # browsing feeds to fetch
    queue = Queues.CRAWLING if conf.crawler.use_queues else Queues.DEFAULT
    feeds = list(fctrl.list_fetchable(conf.crawler.batch_size))
    WORKER_BATCH.labels(worker_type='fetch-feed').observe(len(feeds))
    logger.info('%d to enqueue', len(feeds))
    for feed in feeds:
        logger.debug("%r: scheduling to be fetched on queue:%r",
                     feed, queue.value)
        process_feed.apply_async(args=[feed.id], queue=queue.value)
    # browsing feeds to delete
    feeds_to_delete = list(fctrl.read(status=FeedStatus.to_delete))
    if feeds_to_delete and REDIS_CONN.setnx(JARR_FEED_DEL_KEY, 'true'):
        REDIS_CONN.expire(JARR_FEED_DEL_KEY, LOCK_EXPIRE)
        logger.info('%d to delete, deleting one', len(feeds_to_delete))
        for feed in feeds_to_delete:
            logger.debug("%r: scheduling to be delete", feed)
            feed_cleaner.apply_async(args=[feed.id])
    # applying clusterizer
    queue = Queues.CLUSTERING if conf.crawler.use_queues else Queues.DEFAULT
    for user_id in ArticleController.get_user_id_with_pending_articles():
        if REDIS_CONN.setnx(JARR_CLUSTERIZER_KEY % user_id, 'true'):
            REDIS_CONN.expire(JARR_CLUSTERIZER_KEY % user_id,
                              conf.crawler.clusterizer_delay)
            logger.debug('Scheduling clusterizer for User(%d) on queue:%r',
                         user_id, queue.value)
            clusterizer.apply_async(args=[user_id], queue=queue.value)
    scheduler.apply_async(countdown=conf.crawler.idle_delay)
    metrics_users_any.apply_async()
    metrics_users_active.apply_async()
    metrics_users_long_term.apply_async()
    metrics_articles_unclustered.apply_async()
    observe_worker_result_since(start, 'scheduler', 'ok')
