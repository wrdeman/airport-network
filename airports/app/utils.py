from collections import OrderedDict
from operator import itemgetter

from app import app
from app.graph import Graph, N_degree_partition, Underground


def get_graph(session, key='network'):
    if key not in session or app.debug:
        if key == 'network':
            gr = Graph()
        elif key == 'underground':
            gr = Underground()
        elif key == 'random':
            gr = N_degree_partition()
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
