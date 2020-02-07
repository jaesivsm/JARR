import logging

from ep_celery import celery_app
from jarr.crawler.crawlers.classic import ClassicCrawler
from jarr.bootstrap import conf
from jarr.controllers import FeedController, ClusterController


logger = logging.getLogger(__name__)


@celery_app.task(name='crawler.process_feed')
def process_feed(feed_id):
    ClassicCrawler(FeedController().get(id=feed_id)).fetch()


@celery_app.task(name='crawler.clusterizer')
def clusterizer():
    ClusterController.clusterize_pending_articles()


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

    clusterizer.apply_async()
    scheduler.apply_async()
