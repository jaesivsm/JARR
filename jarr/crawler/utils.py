import logging
from datetime import datetime
from enum import Enum
from functools import wraps
from hashlib import sha256

from jarr.bootstrap import conf, REDIS_CONN
from jarr.metrics import WORKER

logger = logging.getLogger(__name__)
LOCK_EXPIRE = 60 * 60


def observe_worker_result_since(start, method, result):
    duration = (datetime.now() - start).total_seconds()
    WORKER.labels(method=method, result=result).observe(duration)


class Queues(Enum):
    DEFAULT = conf.celery.task_default_queue
    CRAWLING = 'jarr-crawling'
    CLUSTERING = 'jarr-clustering'


def lock(prefix, expire=LOCK_EXPIRE):
    def metawrapper(func):
        @wraps(func)
        def wrapper(args):
            start = datetime.now()
            key = str(args).encode('utf8')
            key = f"lock-{prefix}-{sha256(key).hexdigest()}"
            if REDIS_CONN.setnx(key, 'locked'):
                REDIS_CONN.expire(key, expire)
                try:
                    return func(args)
                except Exception as error:
                    observe_worker_result_since(start, prefix,
                                                error.__class__.__name__)
                    logger.debug('something wrong happen %r', error)
                    raise
                finally:
                    observe_worker_result_since(start, prefix, 'ok')
                    REDIS_CONN.delete(key)
            else:
                observe_worker_result_since(start, prefix, 'skipped')
        return wrapper
    return metawrapper
