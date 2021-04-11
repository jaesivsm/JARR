import logging

from jarr.controllers.abstract import AbstractController
from jarr.models import User
from werkzeug.security import check_password_hash, generate_password_hash

logger = logging.getLogger(__name__)


class UserController(AbstractController):
    _db_cls = User
    _user_id_key = "id"

    @staticmethod
    def _handle_password(attrs):
        if attrs.get("password"):
            attrs["password"] = generate_password_hash(attrs["password"])
        elif "password" in attrs:
            del attrs["password"]

    def check_password(self, username, password):
        user = self.get(login=username)
        if check_password_hash(user.password, password):
            return user

    def create(self, **attrs):
        self._handle_password(attrs)
        return super().create(**attrs)

    def update(self, filters, attrs, return_objs=False, commit=True):
        self._handle_password(attrs)
        return super().update(filters, attrs, return_objs, commit)

    def delete(self, obj_id, commit=True):
        from jarr.controllers import ArticleController, ClusterController
        fltr = {"user_id": obj_id}
        ClusterController(self.user_id).update(fltr, {"main_article_id": None})
        ArticleController(self.user_id).update(fltr, {"cluster_id": None})
        return super().delete(obj_id)
