from __future__ import division
import unittest

from app import app, graph
from flask import session
import networkx as nx
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


class TestPairwise(unittest.TestCase):
    def test_pairwise(self):
        a = [1, 2, 3]
        b = [4, 5, 6]
        c = [6, 7, 8]
        it = [a, b, c]
        pw = list(graph.pairwise(it))
        self.assertListEqual(list(pw[0]), [a, b])
        self.assertListEqual(list(pw[1]), [b, c])


class GraphTest(graph.BaseGraph):
    def build_graph(self):
        self.graph = nx.Graph()
        self.graph.add_edges_from([(1, 2), (2, 3)])


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.gr = GraphTest()

    def test_efficiency(self):
        """ network = a-b-c
        -> norm = 1/N(N-1) = 1/6
        paths=:
        a[b, c] = [1, 2]
        b[a, c] = [1, 1]
        c[a, b] = [2, 1]

        -> sum(1/path) * norm

        a = sum(1, 0.5) * (1/6) = 0.25
        b = sum(1, 1) * (1/6) = 0.3333
        c = sum(0.5, 1) * (1/6) = 0.25

        """
        effs = self.gr.calculate_global_efficiencies()
        ans = [a/6 for a in [1.5, 2., 1.5]]
        self.assertListEqual(effs.values(), ans)

        E = self.gr.global_efficiency()
        self.assertEqual(E, sum(ans))

        v_min = (E - (1/3)) / E
        mx, v = self.gr.vulnerability()
        # the middle node (2) is the most vulnerable
        self.assertEqual(mx, (2, v_min))

    def test_d3_forced_layout(self):
        self.assertRaises(
            NotImplementedError,
            self.gr.d3_forced_layout
        )
        self.gr.node_labels_to_ints()

        # list tuples (index, {'nodeID': index})
        for node in self.gr.graph.nodes(data=True):
            self.assertEqual(node[0], node[1]['nodeID'])

        # get d3 layout and check source and target are present
        # note I have set first label to zero
        edges, nodes = self.gr.d3_forced_layout()
        for pair in graph.pairwise([1, 2, 3]):
            present = False
            for edge in edges:
                if (
                        edge['source'] == pair[0]-1 and
                        edge['target'] == pair[1]-1
                ):
                    present = True
            self.assertTrue(present)


if __name__ == '__main__':
    unittest.main()
