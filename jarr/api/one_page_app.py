from flask_jwt import current_identity, jwt_required
from flask_restplus import Namespace, Resource, fields

from jarr.controllers import ClusterController, FeedController
from jarr.lib.enums import ReadReason

ACCEPTED_LEVELS = {'success', 'info', 'warning', 'error'}
default_ns = Namespace('default', path='/')
list_feeds_model = default_ns.model('ListFeeds', {
        'fid': fields.Integer(),
        'cid': fields.Integer(),
        'ftitle': fields.String(),
        'cname': fields.String(),
})
unreads_model = default_ns.model('Unreads', {
        'fid': fields.Integer(),
        'unread': fields.Integer(default=0),
})
midle_panel_model = default_ns.model('MiddlePanel', {
        'id': fields.Integer(),
        'feeds_id': fields.List(fields.Integer()),
        'categories_id': fields.List(fields.Integer()),
        'main_article_id': fields.Integer(),
        'main_feed_title': fields.String(),
        'main_title': fields.String(),
        'main_date': fields.DateTime(),
        'main_link': fields.String(),
        'liked': fields.Boolean(default=False),
        'read': fields.Boolean(default=False),
})
filter_parser = default_ns.parser()
filter_parser.add_argument('search_str', type=str,
        help='if specify will filter list with the specified string')
filter_parser.add_argument('search_title', type=bool, default=True,
        help='if True, the search_str will be looked for in title')
filter_parser.add_argument('search_content', type=bool, default=False,
        help='if True, the search_str will be looked for in content')
filter_parser.add_argument('filter', type=str,
        choices=['unread', 'liked'], default='unread',
        help='the boolean (unread or liked) filter to apply to clusters')
filter_parser.add_argument('feed_id', type=int,
        help='the parent feed id to filter with')
filter_parser.add_argument('category_id', type=int,
        help='the parent category id to filter with')
mark_as_read_parser = filter_parser.copy()
mark_as_read_parser.add_argument('only_singles', type=bool, default=False,
        help="set to true to mark as read only cluster with one article")


@default_ns.route('/list-feeds')
class ListFeeds(Resource):

    @staticmethod
    @default_ns.response(200, 'OK', model=[midle_panel_model], as_list=True)
    @default_ns.response(401, 'Unauthorized')
    @default_ns.marshal_list_with(list_feeds_model)
    @jwt_required()
    def get():
        """Will list feeds with their category and respective id."""
        ctrl = FeedController(current_identity.id)
        result = []
        fields_name = 'fid', 'cid', 'ftitle', 'cname'
        for line in ctrl.list_w_categ():
            result.append(dict(zip(fields_name, line)))
        return result, 200


@default_ns.route('/unreads')
class Unreads(Resource):

    @staticmethod
    @default_ns.response(200, 'OK', model=[midle_panel_model], as_list=True)
    @default_ns.response(401, 'Unauthorized')
    @default_ns.marshal_list_with(unreads_model)
    @jwt_required()
    def get():
        """Return feeds with count of unread clusters."""
        result = []
        fields_name = 'fid', 'unread'
        for line in ClusterController(current_identity.id).get_unreads():
            result.append(dict(zip(fields_name, line)))
        return result, 200


def _get_filters(in_dict):
    """
    Will extract filters applicable to the JARR controllers.

    Parameters
    ----------
    in_dict: either request.json or request.form depending on the use case

    """
    search_str = in_dict.get('search_str')
    if search_str:
        search_title = in_dict.get('search_title')
        search_content = in_dict.get('search_content')
        filters = []
        if search_title or not filters:
            filters.append({'title__ilike': "%%%s%%" % search_str})
        if search_content:
            filters.append({'content__ilike': "%%%s%%" % search_str})
        if len(filters) == 1:
            filters = filters[0]
        else:
            filters = {"__or__": filters}
    else:
        filters = {}
    if in_dict.get('filter') == 'unread':
        filters['read'] = False
    elif in_dict.get('filter') == 'liked':
        filters['liked'] = True
    for key in 'feed_id', 'category_id':
        if in_dict.get(key) is not None:
            filters[key] = int(in_dict.get(key)) or None
    return filters


@default_ns.route('/clusters')
class Clusters(Resource):

    @staticmethod
    @default_ns.response(200, 'OK', model=[midle_panel_model], as_list=True)
    @default_ns.response(401, 'Unauthorized')
    @default_ns.marshal_list_with(midle_panel_model)
    @default_ns.expect(filter_parser, validate=True)
    @jwt_required()
    def get():
        """Will list all cluster extract for the middle pannel."""
        attrs = filter_parser.parse_args()
        clu_ctrl = ClusterController(current_identity.id)
        return list(clu_ctrl.join_read(**_get_filters(attrs)))


@default_ns.route('/mark-all-as-read')
class MarkClustersAsRead(Resource):

    @staticmethod
    @default_ns.expect(mark_as_read_parser)
    @default_ns.response(401, 'Unauthorized')
    @default_ns.response(200, 'Clusters in filter marked as read',
                         model=[midle_panel_model], as_list=True)
    @default_ns.marshal_list_with(midle_panel_model)
    @jwt_required()
    def put():
        """Will mark all clusters selected by the filter as read."""
        attrs = mark_as_read_parser.parse_args()
        filters = _get_filters(attrs)
        clu_ctrl = ClusterController(current_identity.id)
        clusters = [clu for clu in clu_ctrl.join_read(**filters)
                    if not attrs.get('only_singles')
                        or len(clu['feeds_id']) == 1]
        if clusters:
            clu_ctrl.update({'id__in': [clu['id'] for clu in clusters]},
                            {'read': True,
                             'read_reason': ReadReason.mass_marked})
        return clusters, 200
