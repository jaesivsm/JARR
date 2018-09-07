from flask_restplus import Namespace, Resource, fields
from flask_jwt import jwt_required, current_identity
from werkzeug.exceptions import NotFound, Forbidden
from jarr.api.common import set_model_n_parser, parse_meaningful_params
from jarr.controllers import (FeedController, CategoryController,
        ClusterController)

prout = {'debug': False}
category_ns = Namespace('category', path='/categor',
        description='Category related operation')
parser = category_ns.parser()
model = category_ns.model('Category', {
        'id': fields.Integer(readOnly=True),
})
suffix = "(if your global settings " \
        "and the article's feed settings allows it)"
set_model_n_parser(model, parser, 'cluster_enabled', bool,
        description="will allow article in your feeds and categories to be "
                    "clusterized" + suffix)
set_model_n_parser(model, parser, 'cluster_tfidf_enabled', bool,
        description="will allow article in your feeds and categories to be "
                    "clusterized through document comparison" + suffix)
set_model_n_parser(model, parser, 'cluster_same_category', bool,
        description="will allow article in your feeds and categories to be "
                    "clusterized while beloning to the same category" + suffix)
set_model_n_parser(model, parser, 'cluster_same_feed', bool,
        description="will allow article in your feeds and categories to be "
                    "clusterized while beloning to the same feed" + suffix)

parser_edit = parser.copy()
parser.add_argument('name', type=str, required=True)
set_model_n_parser(model, parser_edit, 'name', str)


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
        return list(CategoryController(current_identity.id).read()), 200


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
        if attrs:
            changed = cctrl.update({'id': category_id}, attrs)
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
