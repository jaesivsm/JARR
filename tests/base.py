import json
import logging
import unittest
from os import path

from flask_testing import TestCase
from werkzeug.exceptions import NotFound

from jarr.bootstrap import REDIS_CONN, Base, conf, init_db, session
from jarr.lib.enums import ClusterReason
from tests.fixtures.filler import populate_db

logger = logging.getLogger('jarr')
DEFAULT_HEADERS = {'Content-Type': 'application/json',
                   'Accept': 'application/json'}


class BaseJarrTest(TestCase):
    _contr_cls = lambda x=1: None
    _application = None

    def create_app(self):
        self.assertTrue(conf.jarr_testing, "configuration not set on testing")
        from jarr.api import create_app
        self._application = create_app(testing=True)
        return self._application

    def assertIn(self, elem, txt):
        self.assertTrue(elem in txt, "%s not in %s" % (elem, txt))

    def assertNotIn(self, elem, txt):
        self.assertFalse(elem in txt, "%s in %s" % (elem, txt))

    def assertNotInCluster(self, article, cluster):
        self.assertNotEqual(article.cluster_id, cluster.id,
                            "article %r cluster %r (because %r)"
                            % (article, article.cluster,
                               article.cluster_reason))

    def assertInCluster(self, article, cluster, reason=ClusterReason.link):
        self.assertEqual(
            article.cluster_id, cluster.id,
            "article %d:%r:%r cluster %d is not %d(main %d:%r)" % (
                article.id, article.entry_id, article.link,
                article.cluster.id, cluster.id, cluster.main_article_id,
                cluster.main_link))
        self.assertEqual(reason, article.cluster_reason)

    def _get_from_contr(self, obj_id, user_id=None):
        return self._contr_cls(user_id).get(id=obj_id)

    def _test_controller_rights(self, obj, user):

        # testing with logged user
        with self._application.test_request_context():
            self.assertEqual(obj, self._get_from_contr(obj.id))
            self.assertEqual(obj, self._get_from_contr(obj.id, user.id))
            self.assertRaises(NotFound, self._get_from_contr, obj.id, 99)
            # fetching non existent object
            self.assertRaises(NotFound, self._get_from_contr, 99, user.id)

        # testing with pure jarr rights management
        self.assertEqual(obj, self._get_from_contr(obj.id))
        self.assertEqual(obj, self._get_from_contr(obj.id, user.id))
        # fetching non existent object
        self.assertRaises(NotFound, self._get_from_contr, 99, user.id)
        # fetching object with inexistent user
        self.assertRaises(NotFound, self._get_from_contr, obj.id, 99)
        # fetching object with wrong user
        self.assertRaises(NotFound, self._get_from_contr, obj.id, user.id + 1)
        self.assertRaises(NotFound, self._contr_cls().delete, 99)
        self.assertRaises(NotFound, self._contr_cls(user.id).delete, 99)
        self.assertEqual(obj.id, self._contr_cls(user.id).delete(obj.id).id)
        self.assertRaises(NotFound, self._contr_cls(user.id).delete, obj.id)

    @staticmethod
    def _drop_all():
        try:
            session.expunge_all()
            session.execute(
                'DROP TABLE IF EXISTS %s CASCADE'
                % ', '.join([('"%s"' % table) if table == 'user' else table
                             for table in list(Base.metadata.tables)]))
            session.commit()
        except Exception:
            logger.exception("Dropping db failed")

    def setUp(self):
        self.assertTrue(conf.jarr_testing, "configuration not set on testing")
        REDIS_CONN.flushdb()
        from jarr.api import get_cached_user
        get_cached_user.cache_clear()
        init_db()
        self._drop_all()
        Base.metadata.create_all()
        populate_db()

    def tearDown(self):
        REDIS_CONN.flushdb()
        from jarr.api import get_cached_user
        get_cached_user.cache_clear()
        self._drop_all()
        session.close()


class JarrFlaskCommon(BaseJarrTest):

    def setUp(self):
        self.assertTrue(conf.jarr_testing, "configuration not set on testing")
        super().setUp()
        self.app = self._application.test_client()

    def assertStatusCode(self, status_code, response):
        self.assertEqual(status_code, response.status_code,
                         "got %d when expecting %d: %r" % (
                             response.status_code, status_code, response.data))

    def get_token_for(self, user):
        auth_res = self.app.post('/auth', data=json.dumps(
                {'login': user, 'password': user}),
                headers=DEFAULT_HEADERS)
        return auth_res.json['access_token']

    def jarr_client(self, method_name, *urn_parts, **kwargs):
        method = getattr(self.app, method_name)
        headers = kwargs.get('headers', DEFAULT_HEADERS.copy()) or {}
        user = kwargs.pop('user', None)
        to_json = kwargs.pop('to_json', True)
        if 'data' in kwargs and to_json:
            kwargs['data'] = json.dumps(kwargs['data'])
        if user is not None:
            headers['Authorization'] = self.get_token_for(user)

        urn = path.join('', *map(str, urn_parts))
        kwargs.pop('timeout', None)  # removing timeout non supported by flask
        kwargs['headers'] = headers
        resp = method(urn, **kwargs)
        resp.encoding = 'utf8'
        return resp


if __name__ == '__main__':
    unittest.main()
