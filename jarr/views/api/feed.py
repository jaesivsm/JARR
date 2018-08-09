from flask_restful import Api

from jarr.bootstrap import conf
from jarr.controllers.feed import DEFAULT_LIMIT, FeedController
from jarr.views.api.common import (PyAggAbstractResource,
        PyAggResourceExisting, PyAggResourceMulti, PyAggResourceNew)
from jarr.views.common import api_permission


class FeedNewAPI(PyAggResourceNew):
    controller_cls = FeedController


class FeedAPI(PyAggResourceExisting):
    controller_cls = FeedController


class FeedsAPI(PyAggResourceMulti):
    controller_cls = FeedController


class FetchableFeedAPI(PyAggAbstractResource):
    controller_cls = FeedController
    attrs = {'limit': {'type': int, 'default': DEFAULT_LIMIT}}

    @api_permission.require(http_exception=403)
    def get(self):
        args = self.reqparse_args(right='read', allow_empty=True)
        result = [feed for feed
                  in self.controller.list_fetchable(**args)]
        return result or None, 200 if result else 204


def load(application):
    api = Api(application, prefix=conf.api_root)

    api.add_resource(FeedNewAPI, '/feed', endpoint='feed_new.json')
    api.add_resource(FeedAPI, '/feed/<int:obj_id>', endpoint='feed.json')
    api.add_resource(FeedsAPI, '/feeds', endpoint='feeds.json')
    api.add_resource(FetchableFeedAPI, '/feeds/fetchable',
                     endpoint='fetchable_feed.json')
