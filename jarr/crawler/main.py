import logging
from datetime import datetime, timedelta
from functools import wraps
from hashlib import sha256

import urllib3

from ep_celery import celery_app
from jarr.bootstrap import REDIS_CONN, conf
from jarr.controllers import (ArticleController, ClusterController,
                              FeedController, UserController)
from jarr.lib.enums import FeedStatus
from jarr.lib.utils import utc_now
from jarr.metrics import USER, WORKER, WORKER_BATCH

urllib3.disable_warnings()
logger = logging.getLogger(__name__)
LOCK_EXPIRE = 60 * 60
JARR_FEED_DEL_KEY = 'jarr.feed-deleting'
JARR_CLUSTERIZER_KEY = 'jarr.clusterizer.%d'


def lock(prefix, expire=LOCK_EXPIRE):
    def metawrapper(func):
        @wraps(func)
        def wrapper(args):
            start = datetime.now()
            key = str(args).encode('utf8')
            key = 'lock-%s-%s' % (prefix, sha256(key).hexdigest())
            if REDIS_CONN.setnx(key, 'locked'):
                REDIS_CONN.expire(key, expire)
                try:
                    return func(args)
                except Exception as error:
                    logger.debug('something wrong happen %r', error)
                    raise
                finally:
                    duration = (datetime.now() - start).total_seconds()
                    WORKER.labels(method=prefix).observe(duration)
                    REDIS_CONN.delete(key)
        return wrapper
    return metawrapper


@celery_app.task(name='crawler.process_feed')
@lock('process-feed')
def process_feed(feed_id):
    crawler = FeedController().get(id=feed_id).crawler
    logger.warning("%r is gonna crawl", crawler)
    crawler.crawl()


@celery_app.task(name='crawler.clusterizer')
@lock('clusterizer')
def clusterizer(user_id):
    logger.warning("Gonna clusterize pending articles")
    ClusterController(user_id).clusterize_pending_articles()
    REDIS_CONN.delete(JARR_CLUSTERIZER_KEY % user_id)


@celery_app.task(name='crawler.feed_cleaner')
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


@celery_app.task(name='jarr.slow-metrics')
def update_slow_metrics():
    uctrl = UserController()
    USER.labels(status='any').set(uctrl.read().count())
    threshold_connection = utc_now() - timedelta(days=conf.feed.stop_fetch)
    threshold_created = utc_now() - timedelta(days=conf.feed.stop_fetch + 1)
    active = uctrl.read(is_active=True,
                        last_connection__ge=threshold_connection)
    USER.labels(status='active').set(active.count())
    long_term = uctrl.read(is_active=True,
                           last_connection__ge=threshold_connection,
                           date_created__lt=threshold_created)
    USER.labels(status='long_term').set(long_term.count())


@celery_app.task(name='crawler.scheduler')
def scheduler():
    logger.warning("Running scheduler")
    start = datetime.now()
    fctrl = FeedController()
    # browsing feeds to fetch
    feeds = list(fctrl.list_fetchable(conf.crawler.batch_size))
    WORKER_BATCH.labels(worker_type='fetch-feed').observe(len(feeds))
    logger.info('%d to enqueue', len(feeds))
    for feed in feeds:
        logger.debug("%r: scheduling to be fetched", feed)
        process_feed.apply_async(args=[feed.id])
    # browsing feeds to delete
    feeds_to_delete = list(fctrl.read(status=FeedStatus.to_delete))
    if feeds_to_delete and REDIS_CONN.setnx(JARR_FEED_DEL_KEY, 'true'):
        REDIS_CONN.expire(JARR_FEED_DEL_KEY, LOCK_EXPIRE)
        logger.info('%d to delete, deleting one', len(feeds_to_delete))
        for feed in feeds_to_delete:
            logger.debug("%r: scheduling to be delete", feed)
            feed_cleaner.apply_async(args=[feed.id])
            break  # only one at a time
    # applying clusterizer
    for user_id in ArticleController.get_user_id_with_pending_articles():
        if not UserController().get(id=user_id).effectivly_active:
            continue
        if REDIS_CONN.setnx(JARR_CLUSTERIZER_KEY % user_id, 'true'):
            REDIS_CONN.expire(JARR_CLUSTERIZER_KEY % user_id,
                              conf.crawler.clusterizer_delay)
            clusterizer.apply_async(args=[user_id])
    scheduler.apply_async(countdown=conf.crawler.idle_delay)
    WORKER.labels(method='scheduler').observe(
            (datetime.now() - start).total_seconds())
    update_slow_metrics.apply_async()
