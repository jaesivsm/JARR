from prometheus_client import CollectorRegistry
from prometheus_distributed_client import Histogram, Counter

REGISTRY = CollectorRegistry()

REQUESTS = Counter('request', 'request', ['type'],
                   namespace='jarr', registry=REGISTRY)

CLUSTERING = Counter('clustering', 'Cluster events',
                     ['event',  # new cluster, add to cluster
                      'article_type', 'feed_type'],
                     namespace='jarr', registry=REGISTRY)

READ = Counter('read', 'Read event', ['article_type', 'feed_type'],
               namespace='jarr', registry=REGISTRY)

FEED_FETCH = Counter('feed_fetch', 'Feed fetching event',
                     ['feed_type', 'result'],
                     namespace='jarr', registry=REGISTRY)

FEED_LATENESS = Histogram('feed_lateness',
                          'observed delta time when fetching feed',
                          ['feed_type'], namespace='jarr', registry=REGISTRY)
