from flask_restplus import Namespace, Resource
from flask_jwt import jwt_required, current_identity
from jarr.controllers import UserController
from jarr.api.common import set_model_n_parser, parse_meaningful_params

user_ns = Namespace('user', description="User related operations (update, "
        "delete and password management)")
user_model = user_ns.model('User', {})
user_parser = user_ns.parser()
set_model_n_parser(user_model, user_parser, 'login', str)
set_model_n_parser(user_model, user_parser, 'email', str)
set_model_n_parser(user_model, user_parser, 'timezone', str)
user_parser.add_argument('password', type=str)


@user_ns.route('')
class UserResource(Resource):

    @user_ns.response(200, 'OK', model=user_model)
    @user_ns.response(401, 'Unauthorized')
    @user_ns.marshal_with(user_model)
    @jwt_required()
    def get(self):
        user = UserController(current_identity.id).get(id=current_identity.id)
        return user, 200

    @user_ns.expect(user_parser)
    @user_ns.response(200, 'Updated', model=user_model)
    @user_ns.response(401, 'Unauthorized')
    @user_ns.marshal_with(user_model)
    @jwt_required()
    def put(self):
        user_id = current_identity.id
        attrs = parse_meaningful_params(user_parser)
        return UserController(user_id).update({'id': user_id}, attrs,
                return_objs=True).first(), 200

    @user_ns.response(204, 'Deleted')
    @user_ns.response(401, 'Unauthorized')
    @jwt_required()
    def delete(self):
        UserController(current_identity.id).delete(current_identity.id)
        return None, 204
