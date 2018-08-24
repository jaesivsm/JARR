import base64
from flask import Response
from flask_restplus import Namespace, Resource, fields
from flask_jwt import jwt_required, current_identity
from werkzeug.exceptions import NotFound, Forbidden
from jarr_common.feed_utils import construct_feed_from
from jarr.bootstrap import conf
from jarr.api.common import set_model_n_parser, parse_meaningful_params
from jarr.controllers import FeedController, ClusterController, IconController

feed_ns = Namespace('feed', description='Feed related operations')
url_parser = feed_ns.parser()
url_parser.add_argument('url', type=str, required=True)
feed_parser = feed_ns.parser()
feed_build_model = feed_ns.model('FeedBuilder', {
        'link': fields.String(),
        'site_link': fields.String(),
        'icon_url': fields.String(),
        'title': fields.String(),
        'description': fields.String(),
})
feed_model = feed_ns.model('Feed', {
        'id': fields.Integer(readOnly=True),
        'unread_cnt': fields.Integer(readOnly=True, default=0,
            description='The number of unread item in this field'),
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
set_model_n_parser(feed_model, feed_parser, 'cluster_enabled', bool,
        description='is clustering enabled whitin this feed')
set_model_n_parser(feed_model, feed_parser, 'cluster_tfidf', bool,
        description='is clustering through document comparison enabled')
set_model_n_parser(feed_model, feed_parser, 'cluster_tfidf_same_cat', bool,
        description='is clustering through document comparison within a '
                    'single category allowed')
set_model_n_parser(feed_model, feed_parser, 'cluster_same_feed', bool,
        description='is clustering several article from the same feed allowed')
set_model_n_parser(feed_model, feed_parser, 'cluster_tfidf_min_score', float,
        default=conf.cluster_tfidf_min_score,
        description='minimum score for clustering with TFIDF algorithm')
set_model_n_parser(feed_model, feed_parser, 'cluster_wake_up', bool,
        description='if true, on clustering if the cluster is already read, '
                    'it will be unread')
set_model_n_parser(feed_model, feed_parser, 'category_id', int)
set_model_n_parser(feed_model, feed_parser, 'site_link', str)
set_model_n_parser(feed_model, feed_parser, 'description', str)
feed_parser_edit = feed_parser.copy()
set_model_n_parser(feed_model, feed_parser_edit, 'title', str)
set_model_n_parser(feed_model, feed_parser_edit, 'link', str)
feed_parser.add_argument('title', type=str, required=True)
feed_parser.add_argument('link', type=str, required=True)
feed_parser.add_argument('icon_url', type=str)


@feed_ns.route('')
class NewFeedResource(Resource):

    @feed_ns.expect(feed_parser, validate=True)
    @feed_ns.response(201, 'Created', model=feed_model)
    @feed_ns.response(400, 'Validation error')
    @feed_ns.response(401, 'Authorization needed')
    @feed_ns.marshal_with(feed_model, code=201, description='Created')
    @jwt_required()
    def post(self):
        "Create an new feed"
        attrs = feed_parser.parse_args()
        return FeedController(current_identity.id).create(**attrs), 201


@feed_ns.route('s')
class ListFeedResource(Resource):

    @feed_ns.response(200, 'OK', model=[feed_model])
    @feed_ns.response(401, 'Authorization needed')
    @feed_ns.marshal_list_with(feed_model)
    @jwt_required()
    def get(self):
        """List all available feeds with their unread counts and a relative
        URL to their icons """
        feeds = []
        user_id = current_identity.id
        cnt_by_feed = ClusterController(user_id).count_by_feed(read=False)
        for feed in FeedController(user_id).read():
            feed.unread_cnt = cnt_by_feed.get(feed.id, 0)
            feeds.append(feed)
        return feeds, 200


@feed_ns.route('/<int:feed_id>')
class FeedResource(Resource):

    @feed_ns.expect(feed_parser_edit)
    @feed_ns.response(204, 'Updated')
    @feed_ns.response(400, 'Validation error')
    @feed_ns.response(401, 'Authorization needed')
    @feed_ns.response(403, 'Forbidden')
    @feed_ns.response(404, 'Not found')
    @jwt_required()
    def put(self, feed_id):
        "Update an existing feed"
        fctrl = FeedController(current_identity.id)
        attrs = parse_meaningful_params(feed_parser_edit)
        changed = fctrl.update({'id': feed_id}, attrs)
        if not changed:
            fctrl.assert_right_ok(feed_id)
        return None, 204

    @feed_ns.response(204, 'Deleted')
    @feed_ns.response(400, 'Validation error')
    @feed_ns.response(401, 'Authorization needed')
    @feed_ns.response(403, 'Forbidden')
    @feed_ns.response(404, 'Not found')
    @jwt_required()
    def delete(self, feed_id):
        "delete an existing feed"
        try:
            FeedController(current_identity.id).delete(feed_id)
        except NotFound:
            if FeedController().get(id=feed_id).user_id != current_identity.id:
                raise Forbidden()
            raise
        return None, 204


@feed_ns.route('/build')
class FeedBuilder(Resource):

    @feed_ns.expect(url_parser, validate=True)
    @feed_ns.response(200, "Pseudo feed constructed", model=feed_build_model)
    @feed_ns.response(406, "Pseudo feed missing link", model=feed_build_model)
    @jwt_required()
    def get(self):
        """Construct a feed from (any) url and send back that field for later
        creation"""
        feed = construct_feed_from(url_parser.parse_args()['url'],
                timeout=conf.crawler.timeout,
                user_agent=conf.crawler.user_agent)
        return feed, 200 if feed.get('link') else 406


@feed_ns.route('/icon')
class Icon(Resource):

    @feed_ns.expect(url_parser, validate=True)
    @feed_ns.response(200, 'OK',
            headers={'Cache-Control': 'max-age=86400',
                     'Content-Type': 'image/*'})
    @feed_ns.response(404, 'Not found')
    def get(self):
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
