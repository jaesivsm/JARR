import logging
from werkzeug import generate_password_hash, check_password_hash
from .abstract import AbstractController
from web.models import User

logger = logging.getLogger(__name__)


class UserController(AbstractController):
    _db_cls = User
    _user_id_key = 'id'

    def _handle_password(self, attrs):
        if attrs.get('password'):
            attrs['password'] = generate_password_hash(attrs.pop('password'))
        elif 'password' in attrs:
            del attrs['password']

    def check_password(self, user, password):
        return check_password_hash(user.password, password)

    def create(self, **attrs):
        self._handle_password(attrs)
        return super().create(**attrs)

    def update(self, filters, attrs, *args, **kwargs):
        self._handle_password(attrs)
        return super().update(filters, attrs, *args, **kwargs)

    def delete(self, obj_id):
        from web.controllers import ClusterController, ArticleController
        ClusterController(self.user_id).update({}, {'main_article_id': None})
        ArticleController(self.user_id).update({}, {'cluster_id': None})
        return super().delete(obj_id)
