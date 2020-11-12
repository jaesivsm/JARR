from prometheus_client import CollectorRegistry
from prometheus_distributed_client import Gauge, Counter, Histogram

REGISTRY = CollectorRegistry()
BUCKETS_3H = [3, 4, 5, 6, 9, 12, 18, 26, 38, 57, 85, 126, 189, 282, 423, 633,
              949, 1423, 2134, 3201, 4801, 7200, 10798]
BUCKETS_7D = [615, 922, 1383, 2073, 3109, 4663, 6994, 10490, 15734, 23600,
              35399, 53098, 79646, 119468, 179201, 268801, 403200, 604798]


READ = Counter('read', 'Read event', ['reason'], namespace='jarr',
               registry=REGISTRY)

FEED_FETCH = Counter('feed_fetch', 'Feed fetching event',
                     ['feed_type', 'result'], namespace='jarr',
                     registry=REGISTRY)

FEED_LATENESS = Histogram('feed_lateness',
                          'observed delta time when fetching feed',
                          ['feed_type'],
                          buckets=BUCKETS_7D,
                          namespace='jarr', registry=REGISTRY)

FEED_EXPIRES = Histogram('feed_expires',
                         'detlta time in second observed when setting expires',
                         ['feed_type', 'method'], buckets=BUCKETS_7D,
                         namespace='jarr', registry=REGISTRY)

WORKER_BATCH = Histogram('worker_batch', 'worker batch size', ['worker_type'],
                         buckets=BUCKETS_3H[:-7], namespace='jarr',
                         registry=REGISTRY)

TFIDF_SCORE = Histogram('tfidf_score', 'TFIDF scores', ['feed_type'],
                        buckets=[i / 100 for i in range(0, 100, 10)],
                        namespace='jarr', registry=REGISTRY)

WORKER = Histogram(
        'worker_method', 'worker taken actions', ['method'],
        buckets=BUCKETS_3H, namespace='jarr', registry=REGISTRY)

EVENT = Counter('event', 'events', ['module', 'context', 'result'],
                namespace='jarr', registry=REGISTRY)

ARTICLE_CREATION = Counter('article_creation', 'Article Creation',
                           ['read', 'read_reason', 'cluster'],
                           namespace='jarr', registry=REGISTRY)

SERVER = Counter('server_method', 'server taken actions',
                 ['uri', 'method', 'result'], namespace='jarr',
                 registry=REGISTRY)

USER = Gauge('users', 'users', ['status'], namespace='jarr', registry=REGISTRY)
