from tests.base import JarrFlaskCommon
from jarr.bootstrap import conf


class UserTest(JarrFlaskCommon):

    def test_FacebookAuthorizeUrl_get(self):
        id_ = conf.oauth.facebook.id = 'TEH_FB_ID'
        conf.oauth.facebook.secret = 'TEH_FB_SECRET'
        resp = self.jarr_client('get', 'oauth', 'facebook')
        self.assertStatusCode(301, resp)
        self.assertIn('graph.facebook', resp.headers['Location'])
        self.assertIn(id_, resp.headers['Location'])

    def test_GoogleAuthorizeUrl_get(self):
        id_ = conf.oauth.google.id = 'TEH_G_ID'
        conf.oauth.google.secret = 'TEH_G_SECRET'
        resp = self.jarr_client('get', 'oauth', 'google')
        self.assertStatusCode(301, resp)
        self.assertIn('https://accounts.google.com/o/oauth2/auth?',
                      resp.headers['Location'])
        self.assertIn(id_, resp.headers['Location'])

    #def test_TwitterAuthorizeUrl_get(self):
    #    resp = self.jarr_client('get', 'oauth', 'twitter', 'authorize_url')
    #    import ipdb
    #    ipdb.sset_trace()
    #    self.assertStatusCode(301, resp)

    def test_LinuxfrAuthorizeUrl_get(self):
        id_ = conf.oauth.linuxfr.id = 'TEH_DLFP_ID'
        conf.oauth.linuxfr.secret = 'TEH_DLFP_SECRET'
        resp = self.jarr_client('get', 'oauth', 'linuxfr')
        self.assertStatusCode(301, resp)
        self.assertIn('https://linuxfr.org/api/oauth/authorize?',
                      resp.headers['Location'])
        self.assertIn(id_, resp.headers['Location'])
