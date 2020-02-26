from prometheus_client import Histogram, Counter

REQUESTS = Counter('request', 'request', ['type'], namespace='jarr')

CLUSTERING = Counter('clustering', 'Cluster events',
                     ['reason'], namespace='jarr')

ARTICLE_CREATION = Counter('article_creation', 'Article Creation',
                           ['article_type'], namespace='jarr')

READ = Counter('read', 'Read event', ['reason'], namespace='jarr')

FEED_FETCH = Counter('feed_fetch', 'Feed fetching event',
                     ['feed_type', 'result'], namespace='jarr')

FEED_LATENESS = Histogram('feed_lateness',
                          'observed delta time when fetching feed',
                          ['feed_type'], namespace='jarr')
