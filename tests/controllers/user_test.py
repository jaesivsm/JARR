from tests.base import BaseJarrTest
from jarr.controllers import UserController


class UserControllerTest(BaseJarrTest):
    _contr_cls = UserController

    def test_password(self):
        passwd = 'test_password'
        ucontr = UserController()
        user = ucontr.create(login=passwd, password=passwd)
        self.assertNotEqual(passwd, user.password)
        self.assertTrue(ucontr.check_password(user, passwd))
        self.assertFalse(ucontr.check_password(user, passwd * 2))
        passwd *= 2
        ucontr.update({'id': user.id}, {'password': passwd})
        user = ucontr.get(id=user.id)
        self.assertNotEqual(passwd, user.password)
        self.assertTrue(ucontr.check_password(user, passwd))
        self.assertFalse(ucontr.check_password(user, passwd * 2))
