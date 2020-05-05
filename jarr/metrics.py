from prometheus_client import Histogram, Counter

READ = Counter('read', 'Read event', ['reason'], namespace='jarr')

FEED_FETCH = Counter('feed_fetch', 'Feed fetching event',
                     ['feed_type', 'result'], namespace='jarr')

FEED_LATENESS = Histogram('feed_lateness',
                          'observed delta time when fetching feed',
                          ['feed_type'], namespace='jarr')

WORKER = Counter('worker_method', 'worker taken actions',
                 ['method'], namespace='jarr')

CLUSTERING = Counter('clustering', 'clustering context and decision',
                     ['filters',  # filter allows clustering or not
                      'config',  # config allows clustering or not
                      'result',  # result is a match or not
                      'match',  # method for the match
                      ], namespace='jarr')

ARTICLE_CREATION = Counter('article_creation', 'Article Creation',
                           ['read', 'read_reason', 'cluster'],
                           namespace='jarr')

SERVER = Counter('server_method', 'server taken actions',
                 ['uri', 'method', 'result'], namespace='jarr')
