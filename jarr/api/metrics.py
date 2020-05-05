from flask import Response
from flask_restx import Namespace, Resource
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from jarr.metrics import REGISTRY

metrics_ns = Namespace('metrics', description="Prometheus metrics")


@metrics_ns.route('')
class Metric(Resource):

    @staticmethod
    def get():
        return Response(generate_latest(REGISTRY),
                        mimetype=CONTENT_TYPE_LATEST)
