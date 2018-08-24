from tests.base import BaseJarrTest
from jarr.controllers import UserController


class UserControllerTest(BaseJarrTest):
    _contr_cls = UserController

    def test_password(self):
        login = 'new_login'
        passwd = 'test_password'
        ucontr = UserController()
        user = ucontr.create(login=login, password=passwd)
        self.assertNotEqual(passwd, user.password)
        self.assertEqual(user, ucontr.check_password(login, passwd))
        self.assertIsNone(ucontr.check_password(login, passwd * 2))
        passwd *= 2
        ucontr.update({'id': user.id}, {'password': passwd})
        user = ucontr.get(id=user.id)
        self.assertNotEqual(passwd, user.password)
        self.assertEqual(user, ucontr.check_password(login, passwd))
        self.assertIsNone(ucontr.check_password(login, passwd * 2))
