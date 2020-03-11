import logging

from ep_celery import celery_app
from jarr.bootstrap import conf
from jarr.controllers import FeedController, ClusterController
from jarr.lib.enums import FeedStatus


logger = logging.getLogger(__name__)


@celery_app.task(name='crawler.process_feed')
def process_feed(feed_id):
    FeedController().get_crawler(feed_id).crawl()


@celery_app.task(name='crawler.clusterizer')
def clusterizer():
    ClusterController.clusterize_pending_articles()


@celery_app.task(name='crawler.feed_cleaner')
def feed_cleaner():
    root_feed_ctrl = FeedController()
    feeds = list(root_feed_ctrl.read(status=FeedStatus.to_delete))
    try:
        root_feed_ctrl.update({'id__in': [feed.id for feed in feeds]},
                              {'status': FeedStatus.deleting})
        for feed in feeds:
            FeedController(feed.user_id).delete(feed.id)
    except Exception:
        logger.exception('something went wrong when deleting feeds %r', feeds)
        root_feed_ctrl.update({'id__in': [feed.id for feed in feeds]},
                              {'status': FeedStatus.to_delete})


@celery_app.task(name='crawler.scheduler')
def scheduler():
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
    scheduler.apply_async()
