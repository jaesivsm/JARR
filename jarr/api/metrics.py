from prometheus_client import generate_latest

from flask_restx import Namespace, Resource
from flask import Response

metrics_ns = Namespace('metrics', description="Prometheus metrics")

@metrics_ns.route('')
class Metric(Resource):

    @staticmethod
    def get():
        return Response(generate_latest(), mimetype='text/plain')
