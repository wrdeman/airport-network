import csv

from flask import jsonify, render_template, request, Response
import networkx as nx

from app import app, vega

with open('data/flights.csv') as f:
    graph = nx.read_weighted_edgelist(f, delimiter=',')

with open('data/airports.csv') as fcsv:
    reader = csv.reader(fcsv, delimiter=',')
    airport_data = {}
    for row in reader:
        # only add airports that are nodes
        if row[0] in nx.nodes(graph):
            airport_data.update({
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


@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html')


@app.route('/map')
def map():
    return jsonify(**vega.BareMap().get_json())


@app.route('/airports')
@app.route('/airports/<airport_code>', methods=['GET', 'DELETE'])
def airports(airport_code=None):
    """ get information on an airport or return all airports
    """
    if request.method == 'GET':
        if airport_code:
            data = airport_data.get(airport_code) or None
            if data:
                data['degree'] = nx.degree_centrality(graph)[airport_code]
                data['eigenvector'] = nx.eigenvector_centrality(
                    graph
                )[airport_code]
            return jsonify(**data)
        else:
            return jsonify(airport_data=airport_data.values())

    elif request.method == 'DELETE':
        if airport_code:
            try:
                graph.remove_node(airport_code)
                return Response("Deleted", status=200)
            except nx.NetworkXError:
                pass
        return Response("Nothing to delete", status=204)


@app.route('/flights')
@app.route('/flights/<departure_code>')
@app.route('/flights/<departure_code>/<destination_code>')
def flights(departure_code=None, destination_code=None):
    if departure_code and destination_code:
        # get shortest paths
        shortest_paths = []
        try:
            paths = nx.all_shortest_paths(
                graph,
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
        neighbors = nx.neighbors(graph, departure_code)
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
        edges = graph.edges(data=True)
        for edge in edges:
            data.append({
                'origin': edge[0],
                'destination': edge[1],
                'count': edge[2]['weight']
            })
        return jsonify(flight_data=data)
