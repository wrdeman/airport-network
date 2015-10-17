import json

import app
from utils import get_actor
from py2neo import Graph, Relationship, Node
import mock

import unittest


class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()

    def tearDown(self):
        pass

    @mock.patch('py2neo.Graph.match')
    @mock.patch('py2neo.Relationship.end_node')
    @mock.patch('py2neo.Node.get_properties')
    @mock.patch('py2neo.Graph.find_one')
    @mock.patch('utils.get_db')
    def test_get_actor(self, get_db, find_one, get_props, rel, match):
        get_db.return_value = Graph()
        get_props.return_value = 0
        rel.return_value = Node()
        match.return_value = iter(
            [Relationship(Node(), 'ACTS_IN', Node())]*2
        )

        ret = {
            'name': 0,
            'title': 0,
            'bio': 0,
            'films': [
                {'title': 'Title', 'film_id': 1},
                {'title': 'Title', 'film_id': 1}
            ]
        }
        res = get_actor('123')
        find_one.assert_called_with('Actor', 'id', '123')

        for k, v in res.iteritems():
            if isinstance(v, dict):
                for kk, vv in v.iteritems():
                    self.assertTrue(kk in ret[k])
            else:
                self.assertTrue(k in ret)

    @mock.patch('py2neo.Graph.find_one')
    @mock.patch('app.utils.get_actor')
    def test_actor_view(self, mock_actor, find_one):
        mock_actor.return_value = {'data': 'data'}
        find_one.return_value = None
        response = self.app.get('/actor/1')
        mock_actor.assert_called_with('1')

        self.assertEquals(response.status_code, 200)
        self.assertDictEqual({'data': 'data'}, json.loads(response.data))


if __name__ == '__main__':
    unittest.main()
