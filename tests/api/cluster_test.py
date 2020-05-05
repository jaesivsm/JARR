from tests.base import JarrFlaskCommon
from jarr.controllers import (UserController, ClusterController,
        ArticleController)


class ClusterApiTest(JarrFlaskCommon):

    def test_ClusterResource_get(self):
        user = UserController().get(login='user1')
        cluster = ClusterController(user.id).read().first()
        resp = self.jarr_client('get', 'cluster', cluster.id)
        self.assertStatusCode(401, resp)
        resp = self.jarr_client('get', 'cluster', cluster.id, user='user2')
        self.assertStatusCode(403, resp)
        resp = self.jarr_client('get', 'cluster', cluster.id, user=user.login)
        self.assertStatusCode(226, resp)
        self.assertEqual(1, len(resp.json['articles']))
        resp = self.jarr_client('get', 'cluster', cluster.id, user=user.login)
        self.assertStatusCode(200, resp)

    def test_ClusterResource_put(self):
        cluster = ClusterController().read().first()
        user = UserController().get(id=cluster.user_id)
        resp = self.jarr_client('put', 'cluster', cluster.id,
                                data={'read': True})
        self.assertStatusCode(401, resp)
        resp = self.jarr_client('put', 'cluster', cluster.id,
                                data={'read': True}, user='user2')
        self.assertStatusCode(403, resp)
        # marking as read
        resp = self.jarr_client('put', 'cluster', cluster.id,
                                data={'read': True}, user=user.login)
        self.assertStatusCode(204, resp)
        cluster = ClusterController().get(id=cluster.id)
        self.assertTrue(cluster.read)
        self.assertFalse(cluster.liked)
        self.assertEqual('marked', cluster.read_reason.value)
        # marking as read / consulted
        resp = self.jarr_client('put', 'cluster', cluster.id,
                                data={'read_reason': 'consulted',
                                      'read': True}, user=user.login)
        self.assertStatusCode(204, resp)
        cluster = ClusterController().get(id=cluster.id)
        self.assertTrue(cluster.read)
        self.assertFalse(cluster.liked)
        self.assertEqual('consulted', cluster.read_reason.value)

        # marking as liked
        resp = self.jarr_client('put', 'cluster', cluster.id,
                                data={'liked': True}, user=user.login)
        self.assertStatusCode(204, resp)
        self.assertTrue(ClusterController().get(id=cluster.id).read)
        self.assertTrue(ClusterController().get(id=cluster.id).liked)

        resp = self.jarr_client('put', 'cluster', cluster.id,
                data={'liked': False, 'read': False}, user=user.login)
        self.assertStatusCode(204, resp)
        self.assertFalse(ClusterController().get(id=cluster.id).read)
        self.assertFalse(ClusterController().get(id=cluster.id).liked)
        self.assertIsNone(ClusterController().get(id=cluster.id).read_reason)

    def test_ClusterResource_delete(self):
        cluster = ClusterController().read().first()
        user = UserController().get(id=cluster.user_id)
        resp = self.jarr_client('delete', 'cluster', cluster.id)
        self.assertStatusCode(401, resp)
        resp = self.jarr_client('delete', 'cluster', cluster.id, user='user2')
        self.assertStatusCode(403, resp)
        resp = self.jarr_client('delete', 'cluster', cluster.id,
                user=user.login)
        self.assertStatusCode(204, resp)

        self.assertEqual(0, ClusterController().read(id=cluster.id).count())
        self.assertEqual(0,
                ArticleController().read(cluster_id=cluster.id).count())
