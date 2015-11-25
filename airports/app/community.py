import networkx as nx
import numpy as np
import scipy as sp


class Tree(object):
    """
    """
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    def add_left(self, a, b):
        self.left = Tree(left=a, right=b)

    def add_right(self, a, b):
        self.left = Tree(left=a, right=b)

    @classmethod
    def get_leaves(cls, tree):
        nodes = []
        if tree:
            if isinstance(tree.left, Tree):
                nodes.append(cls.get_leaves(tree.left))
            else:
                nodes.append(tree.left)
            if isinstance(tree.right, Tree):
                nodes.append(cls.get_leaves(tree.right))
            else:
                nodes.append(tree.right)
        return nodes

    @classmethod
    def get_tree_level(cls, tree, level=0):
        def flatten(L):
            for item in L:
                try:
                    for i in flatten(item):
                        yield i
                except TypeError:
                    yield item

        def split(nodes, i):
            if isinstance(nodes, list):
                return [
                    nd for node in nodes
                    if isinstance(node, list)
                    for nd in node
                ], i+1
            else:
                return [], i+1
        nodes = cls.get_leaves(tree)

        count = 0
        while count < level:
            nodes, count = split(nodes, count)
        return [
            list(flatten(node))
            for node in nodes
            if isinstance(node, list)
        ]


class Graph(object):
    def __init__(self, g=None, B=None, m=None):
        if g:
            self.n = len(list(g.nodes()))
            self.m = len(list(g.edges()))
            self.degs = np.array(dict(nx.degree(g)).values())
            self.B = (
                nx.adjacency_matrix(g) -
                (np.outer(self.degs, self.degs)/(2.*self.m))
            )
        elif isinstance(B, np.ndarray) and m:
            self.B = B
            self.n = len(B)
            self.m = m
        self.s = np.zeros(self.n)

    def _communities_from_vector(self, vector):
        communities = [[], []]
        for i, val in enumerate(vector):
            if np.real(val) >= 0:
                self.s[i] = 1
                communities[0].append(i)
            else:
                communities[1].append(i)
                self.s[i] = -1
        return communities

    def communities(self):
        com1, com2 = [], []
        for i, s in enumerate(self.s):
            if s == 1:
                com1.append(i)
            else:
                com2.append(i)
        return com1, com2

    def Q(self, s):
        return (
            (1./(4.*self.m)) *
            np.dot(np.dot(np.transpose(s), self.B), s)
        )

    def community(self):
        value, vector = sp.sparse.linalg.eigs(self.B, k=1, which='LR')
        if value > 0:
            vector = np.transpose(vector)
            vector = np.array(vector).reshape(-1,).tolist()
            comm = self._communities_from_vector(vector)
            return comm

    def maximise_q(self):
        q = self.Q(self.s)
        mx = [-100, -1]
        for i, s in enumerate(self.s):
            s_new = np.copy(self.s)
            s_new[i] *= -1
            q_new = self.Q(s_new)
            if q_new > mx[0]:
                mx[0] = q_new
                mx[1] = i
        return q, mx[0] - q, mx[1]

    def maximise(self):
        mx = 100
        count = 0
        q_last, _, _ = self.maximise_q()
        while True:
            q, mx_q, mx_i = self.maximise_q()
            if mx_q < 0.00 or count > mx:
                return q_last
            self.s[mx_i] *= -1
            q_last = q
            count += 1
        return q_last

    def get_subB(self, indices):
        ''' get modularity matrix of a subgraph'''
        deleted = list(set([i for i in range(self.n)]) - set(indices))
        sub_b = np.delete(np.delete(self.B, deleted, 0), deleted, 1)
        f_g = np.identity(len(sub_b))*np.sum(sub_b, axis=1)

        sub_m = sum([self.degs[i] for i in indices])
        return sub_b - f_g, sub_m


def get_communities(level=0, g=None):
    def tree_struct(tree, direction, array):
        return {
            'tree': tree,
            'dir': direction,
            'array': array
        }

    if not g:
        g = nx.karate_club_graph()
    graph = Graph(g=g)
    graph.community()
    # initial split
    com1, com2 = graph.communities()

    t = Tree(left=com1, right=com2)
    leaves = [
        tree_struct(t, 'l', t.left),
        tree_struct(t, 'r', t.right)
    ]

    count = 0
    while True:
        if leaves == [] or count > 100:
            break
        new_leaves = []

        for leave in leaves:
            b_sub, m_sub = graph.get_subB(leave['array'])
            try:
                sub_graph = Graph(B=b_sub, m=m_sub)
                sub_graph.community()
            except:
                continue

            if np.max(sub_graph.maximise()) > 0:
                # reassign indices to the original graph
                c1, c2 = sub_graph.communities()
                ntree = Tree(
                    left=[leave['array'][i] for i in c1],
                    right=[leave['array'][i] for i in c2]
                )
                if leave['dir'] == 'l':
                    leave['tree'].left = ntree
                elif leave['dir'] == 'r':
                    leave['tree'].right = ntree
                    new_leaves.extend([
                        tree_struct(ntree, 'l', ntree.left),
                        tree_struct(ntree, 'r', ntree.right)
                    ])
                leaves = new_leaves
            count += 1
    return Tree.get_tree_level(t, level)
