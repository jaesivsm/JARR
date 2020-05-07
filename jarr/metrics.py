from prometheus_client import CollectorRegistry
from prometheus_distributed_client import Counter, Histogram

REGISTRY = CollectorRegistry()

READ = Counter('read', 'Read event', ['reason'], namespace='jarr',
               registry=REGISTRY)

FEED_FETCH = Counter('feed_fetch', 'Feed fetching event',
                     ['feed_type', 'result'], namespace='jarr',
                     registry=REGISTRY)

FEED_LATENESS = Histogram('feed_lateness',
                          'observed delta time when fetching feed',
                          ['feed_type'], namespace='jarr', registry=REGISTRY)

WORKER_BATCH = Histogram('worker_batch', 'worker batch size',
                         ['worker_type'], namespace='jarr', registry=REGISTRY)

WORKER = Counter('worker_method', 'worker taken actions',
                 ['method'], namespace='jarr', registry=REGISTRY)

CLUSTERING = Counter('clustering', 'clustering context and decision',
                     ['filters',  # filter allows clustering or not
                      'config',  # config allows clustering or not
                      'result',  # result is a match or not
                      'match',  # method for the match
                      ], namespace='jarr', registry=REGISTRY)

ARTICLE_CREATION = Counter('article_creation', 'Article Creation',
                           ['read', 'read_reason', 'cluster'],
                           namespace='jarr', registry=REGISTRY)

SERVER = Counter('server_method', 'server taken actions',
                 ['uri', 'method', 'result'], namespace='jarr',
                 registry=REGISTRY)
