from collections import OrderedDict
from operator import itemgetter

import networkx as nx

from app.graph import Graph, Random, Underground


def get_graph(session, key='network'):
    if key not in session:
        if key == 'network':
            gr = Graph()
        elif key == 'underground':
            gr = Underground()
        elif key == 'random':
            gr = Random()
        session[key] = gr
        return gr
    else:
        return session[key]


def sort_degrees(V, limit=None):
    V = OrderedDict(
        sorted(
            V.iteritems(), key=itemgetter(1), reverse=True
        )[:limit]
    )
    return V
