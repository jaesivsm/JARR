from flask_restplus import Namespace, Resource, fields
from flask_jwt import jwt_required, current_identity
from werkzeug.exceptions import NotFound, Forbidden
from jarr.api.common import set_model_n_parser, parse_meaningful_params
from jarr.controllers import (FeedController, CategoryController,
        ClusterController)

prout = {'debug': False}
TO_DENORM = {'cluster_enabled', 'cluster_tfidf', 'cluster_same_feed',
        'cluster_tfidf_same_cat', 'cluster_tfidf_min_score', 'cluster_wake_up'}
category_ns = Namespace('category', path='/categor',
        description='Category related operation')
parser = category_ns.parser()
parser_edit = parser.copy()
parser.add_argument('name', type=str, required=True)
model = category_ns.model('Category', {
        'id': fields.Integer(readOnly=True),
        'unread_cnt': fields.Integer(default=0, readOnly=True),
})
set_model_n_parser(model, parser_edit, 'name', str)
suffix = ' (will be denormed on all feeds below)'
parser_edit.add_argument('cluster_enabled', type=bool,
        help='is clustering enabled whitin this feed' + suffix)
parser_edit.add_argument('cluster_tfidf', type=bool,
        help='is clustering through document comparison enabled' + suffix)
parser_edit.add_argument('cluster_tfidf_same_cat', type=bool,
        help='is clustering through document comparison within a single '
             'category allowed' + suffix)
parser_edit.add_argument('cluster_same_feed', type=bool,
        help='is clustering several article from the same feed allowed'
             + suffix)
parser_edit.add_argument('cluster_tfidf_min_score', type=float,
        help='minimum score for clustering with TFIDF algorithm' + suffix)
parser_edit.add_argument('cluster_wake_up', type=bool,
        help='if true, on clustering if the cluster is already read, '
             'it will be unread' + suffix)


@category_ns.route('y')
class NewCategoryResource(Resource):

    @category_ns.expect(parser, validate=True)
    @category_ns.response(201, 'Created')
    @category_ns.response(400, 'Validation error')
    @category_ns.response(401, 'Authorization needed')
    @category_ns.marshal_with(model, code=201, description='Created')
    @jwt_required()
    def post(self):
        "Create a new category"
        attrs = parse_meaningful_params(parser)
        return CategoryController(current_identity.id).create(**attrs), 201


@category_ns.route('ies')
class ListCategoryResource(Resource):

    @category_ns.response(200, 'OK', model=[model])
    @category_ns.response(401, 'Authorization needed')
    @category_ns.marshal_list_with(model)
    @jwt_required()
    def get(self):
        "List all categories with their unread counts"
        cats = []
        cnt_by_cat = ClusterController(current_identity.id)\
                .count_by_category(read=False)
        for cat in CategoryController(current_identity.id).read():
            cat.unread_cnt = cnt_by_cat.get(cat.id, 0)
            cats.append(cat)
        return cats, 200


@category_ns.route('y/<int:category_id>')
class CategoryResource(Resource):

    @category_ns.expect(parser_edit, validate=True)
    @category_ns.response(204, 'Updated')
    @category_ns.response(400, 'Validation error')
    @category_ns.response(401, 'Authorization needed')
    @category_ns.response(403, 'Forbidden')
    @category_ns.response(404, 'Not found')
    @jwt_required()
    def put(self, category_id):
        "Update an existing category"
        cctrl = CategoryController(current_identity.id)
        attrs = parse_meaningful_params(parser_edit)
        feed_attrs = {key: attrs[key] for key in TO_DENORM.intersection(attrs)}
        attrs = {key: attrs[key] for key in attrs if key not in TO_DENORM}
        changed = 0
        if feed_attrs:
            changed += FeedController(current_identity.id).update(
                    {'category_id': category_id}, feed_attrs)
        if attrs:
            changed += cctrl.update({'id': category_id}, attrs)
        if not changed:
            cctrl.assert_right_ok(category_id)
        return None, 204

    @category_ns.expect(parser)
    @category_ns.response(204, 'Deleted')
    @category_ns.response(400, 'Validation error')
    @category_ns.response(401, 'Authorization needed')
    @category_ns.response(403, 'Forbidden')
    @category_ns.response(404, 'Not found')
    @jwt_required()
    def delete(self, category_id):
        "Delete an existing category"
        try:
            CategoryController(current_identity.id).delete(category_id)
        except NotFound:
            user_id = CategoryController().get(id=category_id).user_id
            if user_id != current_identity.id:
                raise Forbidden()
            raise
        return None, 204
