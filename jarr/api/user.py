from flask_jwt import current_identity, jwt_required
from flask_restx import Namespace, Resource, fields
from werkzeug.exceptions import BadRequest

from jarr.api.common import (parse_meaningful_params, set_clustering_options,
                             set_model_n_parser)
from jarr.controllers import UserController

user_ns = Namespace("user", description="User related operations (update, "
                                        "delete and password management)")
model = user_ns.model("User", {'login': fields.String()})
parser = user_ns.parser()
set_model_n_parser(model, parser, "email", str, nullable=False)
set_model_n_parser(model, parser, "timezone", str, nullable=False)
set_clustering_options("user", model, parser, nullable=False)
parser_edit = parser.copy()
parser_edit.add_argument("password", type=str, nullable=False,
                         store_missing=False)
parser.add_argument("password", type=str, nullable=False, required=True)
parser.add_argument("login", type=str, nullable=False, required=True)


@user_ns.route("")
class UserResource(Resource):

    @staticmethod
    @user_ns.response(200, "OK", model=model)
    @user_ns.response(401, "Unauthorized")
    @user_ns.marshal_with(model)
    @jwt_required()
    def get():
        user = UserController(current_identity.id).get(id=current_identity.id)
        return user, 200

    @staticmethod
    @user_ns.expect(parser, validate=True)
    @user_ns.response(201, "Created", model=model)
    @user_ns.marshal_with(model)
    def post():
        attrs = parse_meaningful_params(parser)
        return UserController().create(**attrs), 201

    @staticmethod
    @user_ns.expect(parser_edit, validate=True)
    @user_ns.response(200, "Updated", model=model)
    @user_ns.response(401, "Unauthorized")
    @user_ns.marshal_with(model)
    @jwt_required()
    def put():
        user_id = current_identity.id
        attrs = parse_meaningful_params(parser_edit)
        if not attrs:
            raise BadRequest()
        return UserController(user_id).update({"id": user_id}, attrs,
                return_objs=True).first(), 200

    @staticmethod
    @user_ns.response(204, "Deleted")
    @user_ns.response(401, "Unauthorized")
    @jwt_required()
    def delete():
        UserController(current_identity.id).delete(current_identity.id)
        return None, 204
