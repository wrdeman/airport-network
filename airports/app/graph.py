import csv
import itertools
import json

import math
import random

from itertools import chain
from collections import OrderedDict
from operator import itemgetter

import networkx as nx
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

    def modularity(self, comm):
        for com in comm:
            for i in com:
                for j in self.graph.node:
                    if i == j:
                        self.graph.edge[i].keys()

    def get_communities(self):
        coms = nx.community.girvan_newman(self.graph)
        mod = {}
        for com in coms:
            partition = {}
            for i, part in enumerate(com):
                for p in part:
                    partition[p] = i

            mod[modularity] = com
            return mod


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
