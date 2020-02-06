from flask_restplus import Namespace, Resource, fields
from flask_jwt import jwt_required, current_identity
from werkzeug.exceptions import NotFound, Forbidden
from jarr.lib.reasons import ReadReason
from jarr.controllers import ClusterController
from jarr.api.common import parse_meaningful_params


cluster_ns = Namespace('cluster', description='Cluster related operations')
cluster_parser = cluster_ns.parser()
cluster_parser.add_argument('liked', type=bool)
cluster_parser.add_argument('read', type=bool)
article_model = cluster_ns.model('Article', {
    'id': fields.Integer(),
    'link': fields.String(),
    'title': fields.String(),
    'content': fields.String(),
    'comments': fields.String(),
    'date': fields.DateTime(),
})

model = cluster_ns.model('Cluster', {
    'id': fields.Integer(),
    'read': fields.Boolean(),
    'liked': fields.Boolean(),
    'content': fields.String(),
    'main_feed_title': fields.String(),
    'main_article_id': fields.Integer(),
    'articles': fields.Nested(article_model, as_list=True),
})


@cluster_ns.route('/<int:cluster_id>')
class ClusterResource(Resource):

    @cluster_ns.marshal_with(model)
    @cluster_ns.response(200, 'OK')
    @cluster_ns.response(226, 'OK, marked as read')
    @cluster_ns.response(400, 'Validation error')
    @cluster_ns.response(401, 'Authorization needed')
    @cluster_ns.response(403, 'Forbidden')
    @cluster_ns.response(404, 'Not found')
    @jwt_required()
    def get(self, cluster_id):
        cluc = ClusterController()
        cluster = cluc.get(id=cluster_id)
        if cluster.user_id != current_identity.id:
            raise Forbidden()
        code = 200
        if not cluster.read:
            cluc.update({'id': cluster_id},
                        {'read': True,
                         'read_reason': ReadReason.read})
            cluster.read = True
            cluster.read_reason = ReadReason.read
            code = 226
        return cluster, code

    @cluster_ns.marshal_with(model)
    @cluster_ns.expect(cluster_parser, validate=True)
    @cluster_ns.response(204, 'Updated')
    @cluster_ns.response(401, 'Authorization needed')
    @cluster_ns.response(403, 'Forbidden')
    @cluster_ns.response(404, 'Not found')
    @jwt_required()
    def put(self, cluster_id):
        cctrl = ClusterController(current_identity.id)
        attrs = parse_meaningful_params(cluster_parser)
        if 'read' in attrs and attrs['read']:
            attrs['read_reason'] = ReadReason.marked
        elif 'read' in attrs and not attrs['read']:
            attrs['read_reason'] = None
        changed = cctrl.update({'id': cluster_id}, attrs)
        if not changed:
            cctrl.assert_right_ok(cluster_id)
        return None, 204

    @cluster_ns.response(204, 'Deleted')
    @cluster_ns.response(400, 'Validation error')
    @cluster_ns.response(401, 'Authorization needed')
    @cluster_ns.response(403, 'Forbidden')
    @cluster_ns.response(404, 'Not found')
    @jwt_required()
    def delete(self, cluster_id):
        try:
            ClusterController(current_identity.id).delete(cluster_id)
        except NotFound:
            user_id = ClusterController().get(id=cluster_id).user_id
            if user_id != current_identity.id:
                raise Forbidden()
            raise
        return None, 204


@cluster_ns.route('/redirect/<int:cluster_id>')
class ClusterRedirectResource(Resource):

    @cluster_ns.response(301, 'Redirect to article')
    @cluster_ns.response(401, 'Authorization needed')
    @cluster_ns.response(403, 'Forbidden')
    @cluster_ns.response(404, 'Not found')
    @jwt_required()
    def get(self, cluster_id):
        cluster = ClusterController().get(id=cluster_id)
        if cluster.user_id != current_identity.id:
            raise Forbidden()
        ClusterController(current_identity.id).update(
                {'id': cluster_id},
                {'read': True, 'read_reason': ReadReason.consulted})
        return None, 301, {'Location': cluster.main_link}
