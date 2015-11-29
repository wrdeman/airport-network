import networkx as nx
import numpy as np
import scipy as sp


def flatten(L):
    """ flatten a list of lists into a generator
    usage list(flatten(list))
    """
    for item in L:
        try:
            for i in flatten(item):
                yield i
        except TypeError:
            yield item


def split(nodes, i):
    """ split the list of lists of lists e.g:
    [[[1,2], [3,4]], [5,6]] -> [[1,2], [3,4], [5,6]]
    """
    if isinstance(nodes, list):
        new = []
        for node in nodes:
            if isinstance(node, list):
                cnt = 0
                while cnt < len(node):
                    nd = node[cnt]
                    if isinstance(nd, list):
                        new.append(nd)
                    else:
                        new.append(node)
                        cnt = len(node)
                    cnt += 1
        return new, i + 1
    else:
        return nodes, i + 1


class Tree(object):
    """
    """
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    def add_left(self, a, b):
        self.left = Tree(left=a, right=b)

    def add_right(self, a, b):
        self.right = Tree(left=a, right=b)

    @classmethod
    def get_leaves(cls, tree):
        """ get an list structure of the tree
        consider
            --|--
          -|-    |
         |   |  | |
        | | | | 5 6
        1 2 3 4

          = [[1,2],[3,4]], [5,6]]

        """
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
        """ method to get the hierarchy.
        consider
            --|--
          -|-    |
         |   |  | |
        | | | | 5 6
        1 2 3 4

        get tree level 0  = [[1,2,3,4], [5,6]]
        get tree level 1  = [1,2],[3,4], [5,6]
        """
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

    def Q(self, s=None, B=None):
        ret_max = False
        if s is None:
            s = self.s
            ret_max = True
        if not isinstance(B, np.ndarray):
            B = self.B
        q = (
            (1./(4.*self.m)) *
            np.dot(np.dot(s, B), s)
        )
        if ret_max:
            return q.max()
        else:
            return q

    def community(self):
        value, vector = sp.sparse.linalg.eigs(self.B, k=1, which='LR')
        if value > 0:
            vector = np.transpose(vector)
            vector = np.array(vector).reshape(-1,).tolist()
            comm = self._communities_from_vector(vector)
            return comm

    def maximise_q(self):
        """ to maximise q change the sign of each element of S and see
        if it results in a larger Q. Instead of iterating through each
        element, define a matrix of S then multiply by matrix of ones
        where the diagonal is -1. i.e. a matrix of S where each element
        is changed. The calculate Q as matrix and get the diagonal which is
        a vector of all the combinations
        """
        d = np.ones([self.n, self.n])
        np.fill_diagonal(d, -1)
        s_combo = self.s * d
        q_combo = self.Q(s=s_combo).diagonal()
        mx_i = q_combo.argmax()
        q_mx = q_combo.max()
        return q_mx, mx_i

    def maximise(self):
        mx = 10
        count = 0
        q_last = self.Q()
        while True:
            mx_q, mx_i = self.maximise_q()
            if mx_q - q_last <= 0.00 or count > mx:
                return q_last
            self.s[mx_i] *= -1
            q_last = mx_q
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

        for leaf in leaves:
            b_sub, m_sub = graph.get_subB(leaf['array'])
            try:
                sub_graph = Graph(B=b_sub, m=m_sub)
                sub_graph.community()
            except:
                continue

            new_Q = sub_graph.maximise()
            print new_Q
            if new_Q > 0:
                # reassign indices to the original graph
                c1, c2 = sub_graph.communities()
                ntree = Tree(
                    left=[leaf['array'][i] for i in c1],
                    right=[leaf['array'][i] for i in c2]
                )
                if leaf['dir'] == 'l':
                    leaf['tree'].left = ntree
                elif leaf['dir'] == 'r':
                    leaf['tree'].right = ntree
                    new_leaves.extend([
                        tree_struct(ntree, 'l', ntree.left),
                        tree_struct(ntree, 'r', ntree.right)
                    ])
            leaves = new_leaves
        count += 1
    return Tree.get_tree_level(t, level)
