from flask_jwt import current_identity, jwt_required
from flask_restx import Namespace, Resource

from jarr.api.common import parse_meaningful_params, set_model_n_parser
from jarr.controllers import UserController

user_ns = Namespace('user', description="User related operations (update, "
        "delete and password management)")
user_model = user_ns.model('User', {})
user_parser = user_ns.parser()
set_model_n_parser(user_model, user_parser, 'login', str, nullable=False)
set_model_n_parser(user_model, user_parser, 'email', str, nullable=False)
set_model_n_parser(user_model, user_parser, 'timezone', str, nullable=False)
suffix = "(if the article feed's and category's settings allows it)"
set_model_n_parser(user_model, user_parser, 'cluster_enabled', bool,
        nullable=False,
        description="will allow article in your feeds and categories to be "
                    "clusterized" + suffix)
set_model_n_parser(user_model, user_parser, 'cluster_tfidf_enabled', bool,
        nullable=False,
        description="will allow article in your feeds and categories to be "
                    "clusterized through document comparison" + suffix)
set_model_n_parser(user_model, user_parser, 'cluster_same_category', bool,
        nullable=False,
        description="will allow article in your feeds and categories to be "
                    "clusterized while beloning to the same category" + suffix)
set_model_n_parser(user_model, user_parser, 'cluster_same_feed', bool,
        nullable=False,
        description="will allow article in your feeds and categories to be "
                    "clusterized while beloning to the same feed" + suffix)
user_parser.add_argument('password', type=str, nullable=False)


@user_ns.route('')
class UserResource(Resource):

    @staticmethod
    @user_ns.response(200, 'OK', model=user_model)
    @user_ns.response(401, 'Unauthorized')
    @user_ns.marshal_with(user_model)
    @jwt_required()
    def get():
        user = UserController(current_identity.id).get(id=current_identity.id)
        return user, 200

    @staticmethod
    @user_ns.expect(user_parser)
    @user_ns.response(200, 'Updated', model=user_model)
    @user_ns.response(401, 'Unauthorized')
    @user_ns.marshal_with(user_model)
    @jwt_required()
    def put():
        user_id = current_identity.id
        attrs = parse_meaningful_params(user_parser)
        return UserController(user_id).update({'id': user_id}, attrs,
                return_objs=True).first(), 200

    @staticmethod
    @user_ns.response(204, 'Deleted')
    @user_ns.response(401, 'Unauthorized')
    @jwt_required()
    def delete():
        UserController(current_identity.id).delete(current_identity.id)
        return None, 204
