from collections import OrderedDict
from operator import itemgetter

import networkx as nx

from app.graph import Graph, Underground


def get_graph(session, key='network'):
    if key not in session:
        if key == 'network':
            gr = Graph()
        elif key == 'underground':
            gr = Underground()
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


def get_current_airports(session):
    """ get a list of airports for drop down boxes based on the current
    graph
    """
    gr = get_graph(session)
    filtered_airports = [
        airport
        for airport in gr.airport_data.values()
        if airport['code'] in nx.nodes(gr.graph)
    ]

    airport_list = OrderedDict()
    for airport in sorted(filtered_airports, key=itemgetter('code')):
        airport_list[airport['code']] = airport['name']

    return airport_list
