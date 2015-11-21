import csv
import itertools
import json

import math
import random

from itertools import chain
from collections import OrderedDict
from operator import itemgetter

import networkx as nx
import numpy as np
from config import get_network_data as get


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


class BaseGraph(object):
    d3 = False

    def __init__(self):
        self.build_graph()

    def build_graph(self):
        raise NotImplementedError

    def calculate_global_efficiencies(self):
        E = {}
        N = self.graph.number_of_nodes()
        norm = 1./(N * (N - 1))

        nodes = nx.shortest_path_length(self.graph)

        for node, paths in nodes:
            E[node] = sum(
                [1./v for k, v in paths.iteritems() if k != node]
            )*norm
        return E

    def global_efficiency(self):
        E = self.calculate_global_efficiencies()
        return sum([eff for node, eff in E.iteritems()])

    def vulnerability(self, limit=None):
        effs = self.calculate_global_efficiencies()
        E = sum([eff for node, eff in effs.iteritems()])
        V = {node: ((E-eff)/E) for node, eff in effs.iteritems()}

        V = OrderedDict(
            sorted(
                V.iteritems(), key=itemgetter(1), reverse=False
            )[0:limit]
        )
        Vmin = V.items()[0]

        return Vmin, V

    @property
    def get_current_nodes(self):
        node_list = OrderedDict()
        for node in sorted(self.graph.node, key=itemgetter(0)):
            node_list[node] = self.graph.node[node]
        return node_list

    def node_labels_to_ints(self):
        ngr = nx.convert_node_labels_to_integers(
            self.graph, first_label=0
        )
        for k, node in ngr.node.iteritems():
            ngr.add_node(
                k,
                nodeID=k
            )
        self.d3 = True
        self.graph = ngr

    def d3_forced_layout(self, data=[]):
        """ extra data is a list of data keys
        """
        if not self.d3:
            raise NotImplementedError

        edges = []
        nodes = []
        edge_ids = []

        for edge in self.graph.edges(data=True):
            extra = {datum: edge[2][datum] for datum in data}
            edges.append({
                'source': edge[0],
                'target': edge[1],
                'data': extra
            })
            edge_ids.extend([edge[0], edge[1]])
        edge_ids = sorted(list(set(edge_ids)))
        for edge_id in edge_ids:
            nodes.append(self.graph.node[edge_id])
        return edges, nodes

    def communities(self):
        communities = [[], []]
        for i, s in enumerate(self.s):
            if s == 1:
                communities[0].append(i)
            else:
                communities[1].append(i)

    def Q(self, s):
        return (1./(4.*self.m))*np.dot(np.dot(np.transpose(s), self.B), s)

    def _community(self):
        self.n = len(list(self.g.nodes()))
        self.m = len(list(self.g.edges()))

        degs = np.array(dict(nx.degree(self.g)).values())
        self.B = (nx.adjacency_matrix(self.g) - (
            np.outer(degs, degs)/(2.*self.m))
        )
        self.s = np.zeros(self.n)

        values, vectors = np.linalg.eig(self.B)
        d = {i: val for i, val in enumerate(values)}
        d = sorted(d.items(), key=itemgetter(1), reverse=True)
        # apparently I need to transpose this?!
        vectors = np.transpose(vectors)
        if d[0][1] > 1e-8:
            vector = np.array(vectors[d[0][0]]).reshape(-1,).tolist()
            comm = self.communities_from_vector(vector)

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

        return mx[0] - q, mx[1]

    def maximise(self):
        mx = 100
        count = 0
        while True:
            print self.Q(self.s)
            mx_q, mx_index = self.maximise_q()
            if mx_q < 0.00 or count > mx:
                break
            self.s[mx_index] *= -1
            count += 1

    def community(self):
        self._community()
        self.maximise()


class Graph(BaseGraph):
    def build_graph(self):
        with open(get('flights')) as f:
            self.graph = nx.read_weighted_edgelist(f, delimiter=',')

        with open(get('airports')) as fcsv:
            next(fcsv)
            reader = csv.reader(fcsv, delimiter=',')

            for row in reader:
                if row[0] in self.graph.nodes():
                    self.graph.add_node(
                        row[0],
                        code=row[0],
                        name=row[1],
                        city=row[2],
                        state=row[3],
                        country=row[4],
                        latitude=row[5],
                        longitude=row[6]
                    )

    @property
    def get_current_nodes(self):
        node_list = OrderedDict()
        for node in sorted(self.graph.node, key=itemgetter(0)):
            node_list[node] = self.graph.node[node]
        return node_list


class Random(BaseGraph):
    def build_graph(self):
        self.graph = nx.random_partition_graph([10, 10], 0, 1)
        self.node_labels_to_ints()


class Karate(BaseGraph):
    def build_graph(self):
        self.graph = nx.karate_club_graph()
        self.node_labels_to_ints()


class N_degree_partition(BaseGraph):
    prune = True
    p = 0.1
    nodes = [50, 50, 50]
    colour = True

    def colour(self):
        for i, part in enumerate(self.graph.graph['partition']):
            for node in part:
                try:
                    self.graph.node[node]['colour'] = i
                except:
                    pass

    def build_graph(self):
        # make a partite network
        self.graph = nx.random_partition_graph(self.nodes, 0, 0)

        if self.p == 0:
            return
        lp = math.log(self.p)

        for p1, p2 in pairwise(self.graph.graph['partition']):
            p1 = sorted(p1)
            p2 = sorted(p2)
            for i in p1:
                for j in p2:
                    if int(self.p) == 1:
                        self.graph.add_edge(i, j)
                        continue
                    lr = math.log(1.0 - random.random())
                    if lr/lp >= 1:
                        self.graph.add_edge(i, j)

        # prune unnconnected nodes
        if self.prune:
            for node in self.graph.nodes():
                if nx.is_isolate(self.graph, node):
                    self.graph.remove_node(node)
        self.node_labels_to_ints()
        self.colour()


class Underground(BaseGraph):
    def build_graph(self):
        self.graph = nx.MultiGraph()
        with open(get('lines')) as f:
            fread = csv.reader(f)
            for edge in fread:
                self.graph.add_edge(edge[0], edge[1], line=edge[2])

        with open(get('stations')) as fs:
            stations = json.load(fs)
            for station in stations:
                # ignore unnconnect stations
                if station['name'] in list(
                        chain.from_iterable(self.graph.edges())
                ):
                    self.graph.add_node(
                        station['name'],
                        name=station["name"],
                        longitude=station["coordinates"][0],
                        latitude=station["coordinates"][1],
                        colour=0
                    )
        self.node_labels_to_ints()

    @property
    def get_current_lines(self):
        return list(
            set(
                nx.get_edge_attributes(self.graph, 'line').values()
            )
        )

    @property
    def get_current_nodes(self):
        return [
            node[1]
            for node in self.graph.nodes(data=True)
            if 'name' in node[1]
        ]
