import unittest
import networkx as nx
import numpy as np
from app.community import Graph, Tree, flatten, Community


class QTestCase(unittest.TestCase):
    def setUp(self):
        self.B = np.array([[1, 1, 1], [1, 1, 1], [2, 3, 4]])
        s = np.ones(3)
        self.g = Graph(B=self.B, m=1)
        self.g.s = s
        self.g.m = 1

    def test_Q(self):

        """
        1/(4m) *  (1,1,1) * ((1,1,1), * (1,
                             (1,1,1),    1,
                             (2,3,4))    1)
        let m = 1 then this is 3.75
        """
        q = self.g.Q(s=self.g.s, B=self.B)
        self.assertEqual(q, 3.75)

    def test_maximise_q(self):
        """ same calculation as above but s = (-1,1,1), (1,-1,1) and
        (1,1-1)
        will be 5/4, 3/4 or 1/4
        mx to be 1.25 at index 0

        """
        q, i = self.g.maximise_q()
        self.assertEqual(1.25, q)
        self.assertEqual(i, 0)

    def test_communitities(self):
        self.g.s = np.array([1, -1, 1])
        c1, c2 = self.g.communities()
        self.assertListEqual([0, 2], c1)
        self.assertListEqual([1], c2)

    def test_vector_communitities(self):
        vec = np.array([0.1, -0.1, 0.9])
        com = self.g._communities_from_vector(vec)
        self.assertListEqual([0, 2], com[0])
        self.assertListEqual([1], com[1])


class TestCommunity(unittest.TestCase):

    def test_community(self):
        size = 3
        graph = nx.barbell_graph(size, 0)
        comgraph = Graph(g=graph)
        comgraph.community()
        c1, c2 = comgraph.communities()
        self.assertEqual(len(c1), len(c2))
        self.assertEqual(len(c1), size)

        # if i want the vector result is len 2
        result = comgraph.community(return_vector=False)
        self.assertTrue(isinstance(result, list))

        result = comgraph.community(return_vector=True)
        self.assertTrue(isinstance(result, tuple))

    def test_community_maximise(self):
        # s is currently [1,1,1,-1,-1,-1]
        # change and maximise will get back to original state
        size = 3
        graph = nx.barbell_graph(size, 0)
        comgraph = Graph(g=graph)
        comgraph.community()
        q = comgraph.Q()
        s_orig = np.copy(comgraph.s)
        s_copy = np.copy(comgraph.s)
        s_copy[1] *= -1
        s_copy[2] *= -1
        comgraph.s = s_copy
        comgraph.maximise()
        self.assertListEqual(list(s_orig), list(comgraph.s))
        self.assertEqual(q, comgraph.Q())


class TestTree(unittest.TestCase):
    def test_flatten(self):
        l = [[1, 2], [3, [4, 5]]]
        l_result = list(flatten(l))
        l_test = [1, 2, 3, 4, 5]
        self.assertListEqual(l_test, l_result)

    def test_tree(self):
        t = Tree(left=1, right=2)
        check_t = Tree.get_leaves(t)
        self.assertListEqual(check_t, [1, 2])

        t.add_left(1, 2)
        t.add_right(3, 4)
        check_t = Tree.get_leaves(t)
        self.assertListEqual(check_t, [[1, 2], [3, 4]])

    def test_leaves(self):
        t = Tree(
            left=Tree(
                left=Tree(
                    left=Tree(left=11, right=12),
                    right=Tree(left=13, right=14)
                ),
                right=Tree(
                    left=Tree(left=21, right=22),
                    right=Tree(left=23, right=24)
                )
            ),
            right=Tree(
                left=Tree(
                    left=Tree(left=31, right=32),
                    right=Tree(left=33, right=34)
                ),
                right=Tree(
                    left=Tree(left=41, right=42),
                    right=Tree(left=43, right=44)
                )
            )
        )

        leaves = Tree.get_tree_level(t, level=0)
        test_leaves = [[11, 12, 13, 14, 21, 22, 23, 24],
                       [31, 32, 33, 34, 41, 42, 43, 44]]
        self.assertListEqual(leaves, test_leaves)

        leaves = Tree.get_tree_level(t, level=1)
        test_leaves = [[11, 12, 13, 14], [21, 22, 23, 24],
                       [31, 32, 33, 34], [41, 42, 43, 44]]
        self.assertListEqual(leaves, test_leaves)

        leaves = Tree.get_tree_level(t, level=2)
        test_leaves = [[11, 12], [13, 14],
                       [21, 22], [23, 24],
                       [31, 32], [33, 34],
                       [41, 42], [43, 44]]
        self.assertListEqual(leaves, test_leaves)

        # uneven tree
        t = Tree(
            left=Tree(
                left=Tree(
                    left=Tree(left=11, right=12),
                    right=Tree(left=13, right=14)
                ),
                right=Tree(
                    left=Tree(left=21, right=22),
                    right=Tree(left=23, right=24)
                )
            ),
            right=Tree(
                left=[31, 32, 33, 34],
                right=[41, 42, 43, 44]
            )
        )
        leaves = Tree.get_tree_level(t, level=0)
        test_leaves = [[11, 12, 13, 14, 21, 22, 23, 24],
                       [31, 32, 33, 34, 41, 42, 43, 44]]
        self.assertListEqual(leaves, test_leaves)

        leaves = Tree.get_tree_level(t, level=1)
        test_leaves = [[11, 12, 13, 14], [21, 22, 23, 24],
                       [31, 32, 33, 34], [41, 42, 43, 44]]
        self.assertListEqual(leaves, test_leaves)

        leaves = Tree.get_tree_level(t, level=20)
        test_leaves = [[11, 12], [13, 14],
                       [21, 22], [23, 24],
                       [31, 32, 33, 34],
                       [41, 42, 43, 44]]
        self.assertListEqual(leaves, test_leaves)


class TestKarate(unittest.TestCase):
    def test_clubsize(self):
        test_graph = Graph(g=nx.karate_club_graph())
        test_graph.community()
        test_q = test_graph.maximise()

        doc_g = nx.karate_club_graph()
        doc = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 16, 17, 19, 21]
        doc_s = [-1] * 34
        for node in doc:
            doc_s[node] *= -1
        doc_graph = Graph(g=doc_g)
        q_doc = doc_graph.Q(s=doc_s)
        self.assertTrue(test_q > q_doc)
