from flask import Blueprint, redirect
from flask_login import current_user, login_required

from jarr_common.reasons import ReadReason
from jarr.controllers import ClusterController

cluster_bp = Blueprint('cluster', __name__, url_prefix='/cluster')


@cluster_bp.route('/redirect/<int:article_id>', methods=['GET'])
@login_required
def redirect_to_article(article_id):
    contr = ClusterController(current_user.id)
    cluster = contr.get(id=article_id)
    if not cluster.read:
        contr.update({'id': cluster.id},
                     {'read': True, 'read_reason': ReadReason.consulted})
    return redirect(cluster.main_article.link)
