import base64

from flask import Response
from flask_jwt import current_identity, jwt_required
from flask_restplus import Namespace, Resource, fields
from werkzeug.exceptions import Forbidden

from jarr.api.common import parse_meaningful_params, set_model_n_parser
from jarr.controllers import (FeedBuilderController, FeedController,
                              IconController)
from jarr.lib.enums import FeedStatus, FeedType

feed_ns = Namespace('feed', description='Feed related operations')
url_parser = feed_ns.parser()
url_parser.add_argument('url', type=str, required=True)
feed_parser = feed_ns.parser()
feed_build_model = feed_ns.model('FeedBuilder', {
        'link': fields.String(),
        'links': fields.List(fields.String()),
        'site_link': fields.String(),
        'feed_type': fields.String(enum=[ft.value for ft in FeedType]),
        'icon_url': fields.String(),
        'title': fields.String(),
        'description': fields.String(),
})
feed_model = feed_ns.model('Feed', {
        'id': fields.Integer(readOnly=True),
        'error_count': fields.Integer(readOnly=True, default=0,
            description='The number of consecutive error encountered while '
                        'fetching this feed'),
        'icon_url': fields.String(readOnly=True,
            description='The complete url to the icon image file'),
        'last_error': fields.String(readOnly=True, default=None,
            description='The last error encountered when fetching this feed'),
        'last_retrieved': fields.DateTime(readOnly=True,
            description='Date of the last time this feed was fetched'),
})
suffix = "(if your global settings " \
        "and the article's category settings allows it)"
set_model_n_parser(feed_model, feed_parser, 'cluster_enabled', bool,
        description="will allow article in your feeds and categories to be "
                    "clusterized" + suffix)
set_model_n_parser(feed_model, feed_parser, 'cluster_tfidf_enabled', bool,
        description="will allow article in your feeds and categories to be "
                    "clusterized through document comparison" + suffix)
set_model_n_parser(feed_model, feed_parser, 'cluster_same_category', bool,
        description="will allow article in your feeds and categories to be "
                    "clusterized while beloning to the same category" + suffix)
set_model_n_parser(feed_model, feed_parser, 'cluster_same_feed', bool,
        description="will allow article in your feeds and categories to be "
                    "clusterized while beloning to the same feed" + suffix)
set_model_n_parser(feed_model, feed_parser, 'cluster_wake_up', bool,
        description='will unread cluster when article '
                    'from that feed are added to it')
set_model_n_parser(feed_model, feed_parser, 'category_id', int)
set_model_n_parser(feed_model, feed_parser, 'site_link', str)
set_model_n_parser(feed_model, feed_parser, 'description', str)
feed_parser_edit = feed_parser.copy()
set_model_n_parser(feed_model, feed_parser_edit, 'title', str)
set_model_n_parser(feed_model, feed_parser_edit, 'status', str,
                   enum=[status.value for status in FeedStatus])
feed_parser.add_argument('title', type=str, required=True)
feed_parser.add_argument('link', type=str, required=True)
feed_parser.add_argument('icon_url', type=str)


@feed_ns.route('')
class NewFeedResource(Resource):

    @staticmethod
    @feed_ns.expect(feed_parser, validate=True)
    @feed_ns.response(201, 'Created', model=feed_model)
    @feed_ns.response(400, 'Validation error')
    @feed_ns.response(401, 'Authorization needed')
    @feed_ns.marshal_with(feed_model, code=201, description='Created')
    @jwt_required()
    def post():
        """Create an new feed."""
        attrs = parse_meaningful_params(feed_parser)
        return FeedController(current_identity.id).create(**attrs), 201


@feed_ns.route('s')
class ListFeedResource(Resource):

    @staticmethod
    @feed_ns.response(200, 'OK', model=[feed_model])
    @feed_ns.response(401, 'Authorization needed')
    @feed_ns.marshal_list_with(feed_model)
    @jwt_required()
    def get():
        """List all available feeds with a relative URL to their icons."""
        return list(FeedController(current_identity.id).read())


@feed_ns.route('/<int:feed_id>')
class FeedResource(Resource):

    @staticmethod
    @feed_ns.expect(feed_parser_edit)
    @feed_ns.response(204, 'Updated')
    @feed_ns.response(400, 'Validation error')
    @feed_ns.response(401, 'Authorization needed')
    @feed_ns.response(403, 'Forbidden')
    @feed_ns.response(404, 'Not found')
    @jwt_required()
    def put(feed_id):
        """Update an existing feed."""
        fctrl = FeedController(current_identity.id)
        attrs = parse_meaningful_params(feed_parser_edit)
        changed = fctrl.update({'id': feed_id}, attrs)
        if not changed:
            fctrl.assert_right_ok(feed_id)
        return None, 204

    @staticmethod
    @feed_ns.response(204, 'Deleted')
    @feed_ns.response(400, 'Validation error')
    @feed_ns.response(401, 'Authorization needed')
    @feed_ns.response(403, 'Forbidden')
    @feed_ns.response(404, 'Not found')
    @jwt_required()
    def delete(feed_id):
        """Delete an existing feed."""
        fctrl = FeedController(current_identity.id)
        if not fctrl.update({'id': feed_id}, {'status': FeedStatus.to_delete}):
            fctrl.assert_right_ok(feed_id)
        return None, 204


@feed_ns.route('/build')
class FeedBuilder(Resource):

    @staticmethod
    @feed_ns.expect(url_parser, validate=True)
    @feed_ns.response(200, "Pseudo feed constructed", model=feed_build_model)
    @feed_ns.response(406, "Pseudo feed missing link", model=feed_build_model)
    @jwt_required()
    def get():
        """
        Construct a feed from (any) url.

        Returns
        -------
        feed:
            a dictionnary with most of what's needed to contruct a feed
            plus alternative links found during parsing

        """
        url = url_parser.parse_args()['url']
        feed = FeedBuilderController(url).construct()
        return feed, 200 if feed.get('link') else 406


@feed_ns.route('/icon')
class Icon(Resource):

    @staticmethod
    @feed_ns.expect(url_parser, validate=True)
    @feed_ns.response(200, 'OK',
                      headers={'Cache-Control': 'max-age=86400',
                               'Content-Type': 'image/*'})
    @feed_ns.response(404, 'Not found')
    def get():
        url = url_parser.parse_args()['url']
        ctr = IconController()
        icon = ctr.get(url=url)
        if icon.content is None:
            ctr.delete(url)
            content = ''
        else:
            content = icon.content

        headers = {'Cache-Control': 'max-age=86400',
                   'Content-Type': icon.mimetype}
        return Response(base64.b64decode(content), headers=headers)
