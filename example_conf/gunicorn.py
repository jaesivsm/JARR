from prometheus_client import (
    CollectorRegistry,
    multiprocess,
    start_http_server,
)


def on_starting(server):
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)

    start_http_server(9100, registry=registry)


def worker_exit(server, worker):
    multiprocess.mark_process_dead(worker.pid)


def child_exit(server, worker):
    multiprocess.mark_process_dead(worker.pid)
