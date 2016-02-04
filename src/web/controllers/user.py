import random
import hashlib
from werkzeug import generate_password_hash, check_password_hash
from .abstract import AbstractController
from web.models import User
import logging
logger = logging.getLogger(__name__)


class UserController(AbstractController):
    _db_cls = User
    _user_id_key = 'id'

    def unset_activation_key(self, obj_id):
        self.update({'id': obj_id}, {'activation_key': ""})

    def set_activation_key(self, obj_id):
        key = str(random.getrandbits(256)).encode("utf-8")
        key = hashlib.sha512(key).hexdigest()[:86]
        self.update({'id': obj_id}, {'activation_key': key})

    def _handle_password(self, attrs):
        if attrs.get('password'):
            attrs['password'] = generate_password_hash(attrs.pop('password'))
        elif 'password' in attrs:
            del attrs['password']

    def check_password(self, user, password):
        return check_password_hash(user.password, password)

    def create(self, **attrs):
        self._handle_password(attrs)
        logger.error(repr(attrs))
        return super().create(**attrs)

    def update(self, filters, attrs):
        self._handle_password(attrs)
        return super().update(filters, attrs)
