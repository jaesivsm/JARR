import logging

from werkzeug.security import check_password_hash, generate_password_hash

from jarr.models import User

from .abstract import AbstractController

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
        from jarr.controllers import ClusterController, ArticleController
        fltr = {'user_id': obj_id}
        ClusterController(self.user_id).update(fltr, {'main_article_id': None})
        ArticleController(self.user_id).update(fltr, {'cluster_id': None})
        return super().delete(obj_id)
