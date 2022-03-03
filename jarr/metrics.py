from prometheus_client import CollectorRegistry
from prometheus_distributed_client import Gauge, Counter, Histogram

REGISTRY = CollectorRegistry()
BUCKETS_3H = [3, 4, 5, 6, 9, 12, 18, 26, 38, 57, 85, 126, 189, 282, 423, 633,
              949, 1423, 2134, 3201, 4801, 7200, 10798]
BUCKETS_7D = [615, 922, 1383, 2073, 3109, 4663, 6994, 10490, 15734, 23600,
              35399, 53098, 79646, 119468, 179201, 268801, 403200, 604798]


def prom(metric_cls, *args, **kwargs):
    return metric_cls(*args, namespace='jarr', registry=REGISTRY, **kwargs)


READ = prom(Counter, 'read', 'Read event', ['reason'])

FEED_FETCH = prom(Counter, 'feed_fetch', 'Feed fetching event',
                  ['feed_type', 'result'])

FEED_LATENESS = prom(Histogram, 'feed_lateness',
                     'observed delta time when fetching feed',
                     ['feed_type'], buckets=BUCKETS_7D)

FEED_EXPIRES = prom(Histogram, 'feed_expires',
                    'detlta time in second observed when setting expires',
                    ['feed_type', 'method'], buckets=BUCKETS_7D)

WORKER_BATCH = prom(Histogram, 'worker_batch', 'worker batch size',
                    ['worker_type'], buckets=BUCKETS_3H[:-7])

TFIDF_SCORE = prom(Histogram, 'tfidf_score', 'TFIDF scores', ['feed_type'],
                   buckets=[i / 100 for i in range(0, 100, 10)])

WORKER = prom(Histogram, 'worker_method', 'worker taken actions',
              ['method', 'result'], buckets=BUCKETS_3H)

EVENT = prom(Counter, 'event', 'events', ['module', 'context', 'result'])

ARTICLE_CREATION = prom(Counter, 'article_creation', 'Article Creation',
                        ['read', 'read_reason', 'cluster'])

SERVER = prom(Counter, 'server_method', 'HTTP method served',
              ['uri', 'method', 'result'])

USER = prom(Gauge, 'users', 'User counts', ['status'])

ARTICLES = prom(Gauge, 'articles', 'Article counts', ['status'])
