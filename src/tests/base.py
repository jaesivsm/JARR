import os
os.environ['JARR_TESTING'] = 'true'

import unittest
from runserver import application
from tests.fixtures import populate_db, reset_db
from flask.ext.login import login_user, logout_user
from werkzeug.exceptions import NotFound


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
            self.assertEquals(obj, self._get_from_contr(obj_id, 99))
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

if __name__ == '__main__':
    unittest.main()
