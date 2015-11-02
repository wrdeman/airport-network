import csv
import json

from collections import OrderedDict
from operator import itemgetter

import networkx as nx


class Graph(object):
    def __init__(self):
        self.build_graph()

    def build_graph(self):
        with open('data/flights.csv') as f:
            self.graph = nx.read_weighted_edgelist(f, delimiter=',')

        with open('data/airports.csv') as fcsv:
            reader = csv.reader(fcsv, delimiter=',')
            self.airport_data = {}
            for row in reader:
                # only add airports that are nodes
                if row[0] in nx.nodes(self.graph):
                    self.airport_data.update({
                        row[0]: {
                            'code': row[0],
                            'name': row[1],
                            'city': row[2],
                            'state': row[3],
                            'country': row[4],
                            'latitude': row[5],
                            'longitude': row[6]
                        }
                    })

    def calculate_global_efficiencies(self):
        E = {}
        N = self.graph.number_of_nodes()
        norm = 1./(N * (N - 1))

        nodes = nx.shortest_path_length(self.graph)
        for node, paths in nodes.iteritems():
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
        Vmax = V.items()[0]

        return Vmax, V


class Underground(Graph):
    def build_graph(self):
        self.tube_lines = []
        self.graph = nx.MultiGraph()
        with open('data/lines.csv') as f:
            fread = csv.reader(f)
            for edge in fread:
                self.graph.add_edge(edge[0], edge[1], line=edge[2])

            self.tube_lines = list(
                set(
                    [edge[2]['line']
                     for edge in self.graph.edges(data=True)]
                )
            )

        with open('data/stations.json') as fs:
            stations = json.load(fs)
            self.station_data = {}
            for station in stations:
                self.station_data.update(
                    {
                        station["name"]: {
                            "name": station["name"],
                            "longitude": station["coordinates"][0],
                            "latitude": station["coordinates"][1]
                        }
                    }
                )
