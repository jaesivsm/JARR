from flask_jwt import current_identity, jwt_required
from flask_restx import Namespace, Resource, fields
from werkzeug.exceptions import Forbidden, NotFound

from jarr.api.common import (parse_meaningful_params, set_clustering_options,
                             set_model_n_parser)
from jarr.controllers import CategoryController

category_ns = Namespace('category', path='/categor',
                        description='Category related operation')
parser = category_ns.parser()
model = category_ns.model("Category", {'id': fields.Integer(readOnly=True)})
set_clustering_options("category", model, parser)
parser_edit = parser.copy()
parser.add_argument('name', type=str, required=True, nullable=False,
                    store_missing=False)
set_model_n_parser(model, parser_edit, 'name', str, nullable=False)


@category_ns.route('y')
class NewCategoryResource(Resource):

    @staticmethod
    @category_ns.expect(parser, validate=True)
    @category_ns.response(201, 'Created')
    @category_ns.response(400, 'Validation error')
    @category_ns.response(401, 'Authorization needed')
    @category_ns.marshal_with(model, code=201, description='Created')
    @jwt_required()
    def post():
        """Create a new category."""
        attrs = parse_meaningful_params(parser)
        return CategoryController(current_identity.id).create(**attrs), 201


@category_ns.route('ies')
class ListCategoryResource(Resource):

    @staticmethod
    @category_ns.response(200, 'OK', model=[model])
    @category_ns.response(401, 'Authorization needed')
    @category_ns.marshal_list_with(model)
    @jwt_required()
    def get():
        """List all categories with their unread counts."""
        return list(CategoryController(current_identity.id).read()), 200


@category_ns.route('y/<int:category_id>')
class CategoryResource(Resource):

    @staticmethod
    @category_ns.response(200, 'OK', model=model)
    @category_ns.response(401, 'Authorization needed')
    @category_ns.marshal_with(model, code=200, description='OK')
    @jwt_required()
    def get(category_id):
        """Read an existing category."""
        return CategoryController(current_identity.id).get(id=category_id), \
                200

    @staticmethod
    @category_ns.expect(parser_edit, validate=True)
    @category_ns.response(204, 'Updated')
    @category_ns.response(400, 'Validation error')
    @category_ns.response(401, 'Authorization needed')
    @category_ns.response(403, 'Forbidden')
    @category_ns.response(404, 'Not found')
    @jwt_required()
    def put(category_id):
        """Update an existing category."""
        cctrl = CategoryController(current_identity.id)
        attrs = parse_meaningful_params(parser_edit)
        if attrs:
            changed = cctrl.update({'id': category_id}, attrs)
            if not changed:
                cctrl.assert_right_ok(category_id)
        return None, 204

    @staticmethod
    @category_ns.expect(parser)
    @category_ns.response(204, 'Deleted')
    @category_ns.response(400, 'Validation error')
    @category_ns.response(401, 'Authorization needed')
    @category_ns.response(403, 'Forbidden')
    @category_ns.response(404, 'Not found')
    @jwt_required()
    def delete(category_id):
        """Delete an existing category."""
        try:
            CategoryController(current_identity.id).delete(category_id)
        except NotFound:
            user_id = CategoryController().get(id=category_id).user_id
            if user_id != current_identity.id:
                raise Forbidden()
            raise
        return None, 204
