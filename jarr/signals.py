import logging

from blinker import signal

from jarr.metrics import EVENT

event = signal('jarr-event')


@event.connect
def bump_metric(sender, **kwargs):
    EVENT.labels(**{key: kwargs[key] for key in ('module', 'context',
                                                 'result')}).inc()


@event.connect
def log(sender, level=logging.DEBUG, **kwargs):
    logger = logging.getLogger(kwargs['module'])
    logger.info("%s > %r: %s",
                kwargs['module'], kwargs["context"], kwargs["result"])
