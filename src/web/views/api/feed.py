import conf
from flask import current_app
from flask.ext.restful import Api

from web.views.common import api_permission
from web.controllers.feed import FeedController, DEFAULT_LIMIT

from web.views.api.common import PyAggAbstractResource, \
                                 PyAggResourceNew, \
                                 PyAggResourceExisting, \
                                 PyAggResourceMulti


class FeedNewAPI(PyAggResourceNew):
    controller_cls = FeedController


class FeedAPI(PyAggResourceExisting):
    controller_cls = FeedController


class FeedsAPI(PyAggResourceMulti):
    controller_cls = FeedController


class FetchableFeedAPI(PyAggAbstractResource):
    controller_cls = FeedController
    attrs = {'max_error': {'type': int, 'default': conf.FEED_ERROR_MAX},
             'limit': {'type': int, 'default': DEFAULT_LIMIT},
             'refresh_rate': {'type': int, 'default': conf.FEED_REFRESH_RATE}}

    @api_permission.require(http_exception=403)
    def get(self):
        args = self.reqparse_args(right='read', allow_empty=True)
        result = [feed for feed
                  in self.controller.list_fetchable(**args)]
        return result or None, 200 if result else 204


api = Api(current_app, prefix=conf.API_ROOT)

api.add_resource(FeedNewAPI, '/feed', endpoint='feed_new.json')
api.add_resource(FeedAPI, '/feed/<int:obj_id>', endpoint='feed.json')
api.add_resource(FeedsAPI, '/feeds', endpoint='feeds.json')
api.add_resource(FetchableFeedAPI, '/feeds/fetchable',
                 endpoint='fetchable_feed.json')
