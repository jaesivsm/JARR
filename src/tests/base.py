import os
os.environ['JARR_TESTING'] = 'true'

import json
import logging
import unittest
from os import path
from base64 import b64encode
from runserver import application
from tests.fixtures.filler import populate_db, reset_db
from flask.ext.login import login_user, logout_user
from werkzeug.exceptions import NotFound

import conf

logger = logging.getLogger('web')


class BaseJarrTest(unittest.TestCase):
    _contr_cls = None

    def _get_from_contr(self, obj_id, user_id=None):
        return self._contr_cls(user_id).get(id=obj_id).dump()

    def _test_controller_rights(self, obj, user):
        obj_id = obj['id']

        # testing with logged user
        with application.test_request_context():
            login_user(user)
            self.assertEquals(obj, self._get_from_contr(obj_id))
            self.assertEquals(obj, self._get_from_contr(obj_id, user.id))
            self.assertRaises(NotFound, self._get_from_contr, obj_id, 99)
            # fetching non existent object
            self.assertRaises(NotFound, self._get_from_contr, 99, user.id)
            logout_user()

        # testing with pure jarr rights management
        self.assertEquals(obj, self._get_from_contr(obj_id))
        self.assertEquals(obj, self._get_from_contr(obj_id, user.id))
        # fetching non existent object
        self.assertRaises(NotFound, self._get_from_contr, 99, user.id)
        # fetching object with inexistent user
        self.assertRaises(NotFound, self._get_from_contr, obj_id, 99)
        # fetching object with wrong user
        self.assertRaises(NotFound, self._get_from_contr, obj_id, user.id + 1)
        self.assertRaises(NotFound, self._contr_cls().delete, 99)
        self.assertRaises(NotFound, self._contr_cls(user.id).delete, 99)
        self.assertEquals(obj['id'],
                self._contr_cls(user.id).delete(obj_id).id)
        self.assertRaises(NotFound, self._contr_cls(user.id).delete, obj_id)

    def setUp(self):
        reset_db()
        populate_db()


class JarrFlaskCommon(BaseJarrTest):

    def setUp(self):
        super().setUp()
        application.config['CSRF_ENABLED'] = False
        application.config['WTF_CSRF_ENABLED'] = False
        self.app = application.test_client()

    def _api(self, method_name, *urn_parts, **kwargs):
        method = getattr(self.app, method_name)
        kwargs['headers'] = {'Content-Type': 'application/json'}
        if 'data' in kwargs and not isinstance(kwargs['data'], str):
            kwargs['data'] = json.dumps(kwargs['data'])
        if 'user' in kwargs:
            hash_ = bytes('%s:%s' % (kwargs['user'], kwargs['user']), 'utf8')
            hash_ = b64encode(hash_).decode('utf8')
            kwargs['headers']['Authorization'] = 'Basic %s' % hash_
            del kwargs['user']

        urn = path.join(conf.API_ROOT, *map(str, urn_parts))
        resp = method(urn, **kwargs)
        if resp.data and resp.content_type == 'application/json':
            resp.json = lambda *a, **kw: json.loads(resp.data.decode('utf8'))
        return resp


if __name__ == '__main__':
    unittest.main()
