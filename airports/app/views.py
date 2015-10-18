from collections import OrderedDict
from operator import itemgetter

from flask import jsonify, render_template, request, Response
import networkx as nx

from app import app, vega
from app.graph import Graph


gr = Graph()


def sort_degrees(V, limit=None):
    V = OrderedDict(
        sorted(
            V.iteritems(), key=itemgetter(1), reverse=True
        )[:limit]
    )
    return V


@app.route('/')
@app.route('/index')
def index():
    _, v = gr.vulnerability(limit=5)

    filtered_airports = [
        airport
        for airport in gr.airport_data.values()
        if airport['code'] in nx.nodes(gr.graph)
    ]

    airport_list = OrderedDict()
    for airport in sorted(filtered_airports, key=itemgetter('code')):
        airport_list[airport['code']] = airport['name']

    return render_template(
        'home.html',
        airports=airport_list,
        degrees=sort_degrees(
            nx.degree_centrality(gr.graph), limit=5
        ),
        eigens=sort_degrees(
            nx.eigenvector_centrality(gr.graph), limit=5
        ),
        vulnerability=v
    )


@app.route('/map')
def map():
    return jsonify(**vega.BareMap().get_json())


@app.route('/airports', methods=['GET', 'POST'])
@app.route('/airports/<airport_code>', methods=['GET', 'DELETE'])
def airports(airport_code=None):
    """ get information on an airport or return all airports
    """
    global gr
    if request.method == 'GET':
        if airport_code:
            data = gr.airport_data.get(airport_code) or None
            if data:
                data['degree'] = nx.degree_centrality(gr.graph)[airport_code]
                data['eigenvector'] = nx.eigenvector_centrality(
                    gr.graph
                )[airport_code]
            return jsonify(**data)
        else:
            return jsonify(airport_data=gr.airport_data.values())

    elif request.method == 'DELETE':
        if airport_code:
            try:
                gr.graph.remove_node(airport_code)
                return Response("Deleted", status=200)
            except nx.NetworkXError:
                pass
        return Response("Nothing to delete", status=204)

    elif request.method == 'POST':
        # using this to refresh the graph
        gr = Graph()
        return Response("Restored", status=200)


@app.route('/flights')
@app.route('/flights/<departure_code>')
@app.route('/flights/<departure_code>/<destination_code>')
def flights(departure_code=None, destination_code=None):
    if departure_code and destination_code:
        # get shortest paths
        shortest_paths = []
        try:
            paths = nx.all_shortest_paths(
                gr.graph,
                departure_code,
                destination_code
            )
        except:
            paths = []
        for path in paths:
            # path is [a,b,c] and need [a, b] [
            shortest_paths.extend(
                [
                    {
                        'origin': path[i],
                        'destination': path[i+1],
                        'count': 1000
                    }
                    for i, _ in enumerate(path[:-1])
                ]
            )
        return jsonify(flight_data=shortest_paths)
    elif departure_code:
        # get next stop
        neighbors = nx.neighbors(gr.graph, departure_code)
        neighbors = [
            {
                'origin': departure_code,
                'destination': dst,
                'count': 20
            }
            for dst in neighbors
        ]
        return jsonify(flight_data=neighbors)
    else:
        data = []
        # get all flights
        edges = gr.graph.edges(data=True)
        for edge in edges:
            data.append({
                'origin': edge[0],
                'destination': edge[1],
                'count': edge[2]['weight']
            })
        return jsonify(flight_data=data)
