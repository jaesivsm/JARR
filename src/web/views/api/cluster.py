from flask_restful import Api

from bootstrap import conf
from web.controllers import ClusterController
from web.views.api.common import (PyAggResourceExisting, PyAggResourceMulti,
                                  PyAggResourceNew)


class ClusterNewAPI(PyAggResourceNew):
    controller_cls = ClusterController


class ClusterAPI(PyAggResourceExisting):
    controller_cls = ClusterController


class ClustersAPI(PyAggResourceMulti):
    controller_cls = ClusterController


def load(application):
    api = Api(application, prefix=conf.API_ROOT)
    api.add_resource(ClusterNewAPI, '/cluster', endpoint='cluster_new.json')
    api.add_resource(ClusterAPI, '/cluster/<int:obj_id>',
                     endpoint='cluster.json')
    api.add_resource(ClustersAPI, '/clusters', endpoint='clusters.json')
