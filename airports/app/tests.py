import unittest

from app import app
from session import session_setup

app = session_setup(app)


class ViewTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestingConfig')
        app.config['SECRET_KEY'] = 'sekrit!'
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_homepage(self):
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, 200)
        # assert 'network' in self.app.session

if __name__ == '__main__':
    unittest.main()
