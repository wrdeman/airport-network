import unittest

from app import app
from flask import session
from session import session_setup

app = session_setup(app)


class ViewTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestingConfig')
        app.config['SECRET_KEY'] = 'sekrit!'
        self.client = app.test_client()

    def tearDown(self):
        pass

    def test_homepage(self):
        with app.test_client() as c:
            resp = c.get('/')
            self.assertEqual(resp.status_code, 200)
            assert 'network' in session

    def test_route(self):
        with app.test_client() as c:
            resp = c.get('/route')
            self.assertEqual(resp.status_code, 200)

    def test_london(self):
        with app.test_client() as c:
            resp = c.get('/london')
            self.assertEqual(resp.status_code, 200)

    def test_map(self):
        with app.test_client() as c:
            resp = c.get('/map')
            self.assertEqual(resp.status_code, 200)

        with app.test_client() as c:
            resp = c.get('/map/AAA')
            self.assertEqual(resp.status_code, 404)

        with app.test_client() as c:
            resp = c.get('/map/AAA/BBB')
            self.assertEqual(resp.status_code, 200)

    def test_histogram(self):
        with app.test_client() as c:
            resp = c.get('/histogram/network')
            self.assertEqual(resp.status_code, 200)

        with app.test_client() as c:
            resp = c.get('/histogram/fail')
            self.assertEqual(resp.status_code, 404)

    def test_airports(self):
        with app.test_client() as c:
            resp = c.get('/airports')
            self.assertEqual(resp.status_code, 200)

            resp = c.get('/airports/AAA')
            self.assertEqual(resp.status_code, 200)

            # bad code returns 404
            resp = c.get('/airports/AAB')
            self.assertEqual(resp.status_code, 404)

            resp = c.delete('/airports/BBB')
            self.assertEqual(resp.status_code, 200)

            resp = c.delete('/airports/BBB')
            self.assertEqual(resp.status_code, 204)

            resp = c.post('/airports')
            self.assertEqual(resp.status_code, 200)

    def test_flights(self):
        with app.test_client() as c:
            resp = c.get('/flights')
            self.assertEqual(resp.status_code, 200)

            resp = c.get('/flights/AAA')
            self.assertEqual(resp.status_code, 200)

            resp = c.get('/flights/AAB')
            self.assertEqual(resp.status_code, 404)

            resp = c.get('/flights/AAA/BBB')
            self.assertEqual(resp.status_code, 200)

            resp = c.get('/flights/AAA/BBC')
            self.assertEqual(resp.status_code, 404)

    def test_degree(self):
        with app.test_client() as c:
            resp = c.get('/degree')
            self.assertEqual(resp.status_code, 404)

            resp = c.get('/degree/scatter/network')
            self.assertEqual(resp.status_code, 200)

            resp = c.get('/degree/fail')
            self.assertEqual(resp.status_code, 404)

            resp = c.get('/degree/scatter/fail')
            self.assertEqual(resp.status_code, 404)


if __name__ == '__main__':
    unittest.main()
