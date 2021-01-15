import base64

from flask import Response
from flask_jwt import current_identity, jwt_required
from flask_restx import Namespace, Resource, fields

from jarr.api.common import (EnumField, parse_meaningful_params,
                             set_clustering_options, set_model_n_parser)
from jarr.controllers import (FeedBuilderController, FeedController,
                              IconController)
from jarr.lib.enums import FeedStatus, FeedType
from jarr.lib.filter import FiltersAction, FiltersTrigger, FiltersType

feed_ns = Namespace('feed', description='Feed related operations')
url_parser = feed_ns.parser()
url_parser.add_argument('url', type=str, required=True,
                        nullable=False, store_missing=False)
filter_model = feed_ns.model('Filter', {
        'action': EnumField(FiltersAction),
        'pattern': fields.String(),
        'action on': EnumField(FiltersTrigger),
        'type': EnumField(FiltersType),
})
parser = feed_ns.parser()
feed_build_model = feed_ns.model('FeedBuilder', {
        'link': fields.String(),
        'links': fields.List(fields.String()),
        'site_link': fields.String(),
        'feed_type': EnumField(FeedType),
        'icon_url': fields.String(),
        'title': fields.String(),
        'description': fields.String(),
        'cluster_enabled': fields.Boolean(default=True, required=True),
        'cluster_tfidf_enabled': fields.Boolean(default=True, required=True),
        'cluster_same_category': fields.Boolean(default=True, required=True),
        'cluster_same_feed': fields.Boolean(default=True, required=True),
        'cluster_wake_up': fields.Boolean(default=True, required=True),
        'same_link_count': fields.Integer(default=0, required=True,
            help='number of feed with same link existing for that user'),
})
# read only fields (and filters which are handled in a peculiar way)
model = feed_ns.model('Feed', {
        'id': fields.Integer(readOnly=True),
        'icon_url': fields.String(readOnly=True,
            description='The complete url to the icon image file'),
        'last_retrieved': fields.DateTime(readOnly=True,
            description='Date of the last time this feed was fetched'),
        'filters': fields.Nested(filter_model, as_list=True),
})
parser.add_argument('filters', type=list, location='json', nullable=False,
                    store_missing=False)
# clustering options
set_clustering_options("feed", model, parser)
set_model_n_parser(model, parser, 'truncated_content', bool, nullable=False)
set_model_n_parser(model, parser, 'feed_type', FeedType, nullable=False)
set_model_n_parser(model, parser, 'category_id', int, nullable=False)
set_model_n_parser(model, parser, 'site_link', str, nullable=False)
set_model_n_parser(model, parser, 'link', str, nullable=False)
set_model_n_parser(model, parser, 'description', str, nullable=False)
set_model_n_parser(model, parser, 'icon_url', str, nullable=False)
parser_edit = parser.copy()
set_model_n_parser(model, parser_edit, 'title', str, nullable=False)
set_model_n_parser(model, parser_edit, 'status', FeedStatus,
                   nullable=False)
parser.add_argument('title', type=str, required=True,
                    nullable=False, store_missing=False)
parser.add_argument('link', type=str, required=True,
                    nullable=False, store_missing=False)
parser.add_argument('icon_url', type=str, required=False,
                    nullable=True, store_missing=False)
set_model_n_parser(model, parser_edit, "error_count", int, nullable=False,
                   description="The number of consecutive error encountered "
                               "while fetching this feed")
set_model_n_parser(model, parser_edit, "last_error", str, nullable=True,
                   description="The last error encountered when fetching "
                               "this feed")


@feed_ns.route('')
class NewFeedResource(Resource):

    @staticmethod
    @feed_ns.expect(parser, validate=True)
    @feed_ns.response(201, 'Created', model=model)
    @feed_ns.response(400, 'Validation error')
    @feed_ns.response(401, 'Authorization needed')
    @feed_ns.marshal_with(model, code=201, description='Created')
    @jwt_required()
    def post():
        """Create an new feed."""
        attrs = parse_meaningful_params(parser)
        return FeedController(current_identity.id).create(**attrs), 201


@feed_ns.route('s')
class ListFeedResource(Resource):

    @staticmethod
    @feed_ns.response(200, 'OK', model=[model])
    @feed_ns.response(401, 'Authorization needed')
    @feed_ns.marshal_list_with(model)
    @jwt_required()
    def get():
        """List all available feeds with a relative URL to their icons."""
        return list(FeedController(current_identity.id).read())


@feed_ns.route('/<int:feed_id>')
class FeedResource(Resource):

    @staticmethod
    @feed_ns.response(200, 'OK', model=model)
    @feed_ns.response(400, 'Validation error')
    @feed_ns.response(401, 'Authorization needed')
    @feed_ns.marshal_with(model, code=200, description='OK')
    @jwt_required()
    def get(feed_id):
        """Read an existing feed."""
        return FeedController(current_identity.id).get(id=feed_id), 200

    @staticmethod
    @feed_ns.expect(parser_edit)
    @feed_ns.response(204, 'Updated')
    @feed_ns.response(400, 'Validation error')
    @feed_ns.response(401, 'Authorization needed')
    @feed_ns.response(403, 'Forbidden')
    @feed_ns.response(404, 'Not found')
    @jwt_required()
    def put(feed_id):
        """Update an existing feed."""
        fctrl = FeedController(current_identity.id)
        attrs = parse_meaningful_params(parser_edit)
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
        code = 406
        url = url_parser.parse_args()['url']
        feed = FeedBuilderController(url).construct()
        if feed.get('link'):
            code = 200
            fctrl = FeedController(current_identity.id)
            feed['same_link_count'] = fctrl.read(link=feed.get('link')).count()
        return feed, code


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
