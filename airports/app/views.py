from collections import Counter

from flask import (
    abort,
    jsonify,
    render_template,
    request,
    Response,
    session,
)

import networkx as nx
import numpy as np

from app import app, utils, vega


@app.route('/')
@app.route('/index')
def index():
    gr = utils.get_graph(session)
    _, v = gr.vulnerability(limit=5)
    airport_list = utils.get_current_airports(session)

    degrees = utils.sort_degrees(
        nx.degree_centrality(gr.graph), limit=5
    )
    try:
        eigens = utils.sort_degrees(
            nx.eigenvector_centrality(gr.graph), limit=5
        )
    except:
        eigens = {}

    return render_template(
        'home.html',
        airports=airport_list,
        degrees=degrees,
        eigens=eigens,
        vulnerability=v
    )


@app.route('/route')
def route():
    airport_list = utils.get_current_airports(session)
    return render_template(
        'route.html',
        airports=airport_list,
    )


@app.route('/london')
def london():
    gr = utils.get_graph(session, key='underground')
    _, v = gr.vulnerability(limit=5)

    stations = gr.station_data
    lines = gr.tube_lines
    return render_template(
        'london.html',
        stations=stations,
        lines=lines,
        degrees=utils.sort_degrees(
            nx.degree_centrality(gr.graph), limit=5
        ),
        vulnerability=v
    )


# vega views
@app.route('/map')
@app.route('/map/<departure_code>/<destination_code>')
def map(departure_code=None, destination_code=None):
    return jsonify(
        **vega.BareMap().get_json(
            **{'src': departure_code, 'dst': destination_code}
        )
    )


@app.route('/histogram/<network>')
def histogram(network='network'):
    if network not in ['network', 'underground']:
        abort(404)
    return jsonify(
        **vega.Scatter().get_json(**{'network': network})
    )


@app.route('/london_map')
@app.route('/london_map/<line>')
def london_map(line=None):
    gr = utils.get_graph(session, key='underground')
    lines = gr.tube_lines
    if line not in lines:
        abort(404)
    return jsonify(
        **vega.LondonMap().get_json(**{'line': line})
    )


@app.route('/london_forced')
def london_forced():
    return jsonify(
        **vega.LondonForced().get_json()
    )


# APIs
@app.route('/airports', methods=['GET', 'POST'])
@app.route('/airports/<airport_code>', methods=['GET', 'DELETE'])
def airports(airport_code=None):
    """ get information on an airport or return all airports
    """
    gr = utils.get_graph(session)
    if request.method == 'GET':
        if airport_code:
            data = gr.airport_data.get(airport_code) or None
            if data:
                data['degree'] = nx.degree_centrality(
                    gr.graph
                )[airport_code]
                # eigenvector centrality sometimes won't converge
                try:
                    eigens = nx.eigenvector_centrality(
                        gr.graph
                    )[airport_code]
                except:
                    eigens = 0
                data['eigenvector'] = eigens
                return jsonify(**data)
            else:
                abort(404)
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
        if 'network' in session:
            session.pop('network', None)
        gr = utils.get_graph(session)
        return Response("Restored", status=200)


@app.route('/flights')
@app.route('/flights/<departure_code>')
@app.route('/flights/<departure_code>/<destination_code>')
def flights(departure_code=None, destination_code=None):
    gr = utils.get_graph(session)
    airports = gr.airport_data.keys()
    if departure_code and departure_code not in airports:
        abort(404)

    if destination_code and destination_code not in airports:
        abort(404)

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


@app.route('/stations', methods=['GET'])
def stations():
    gr = utils.get_graph(session, key='underground')
    return jsonify(stations=gr.station_data.values())


@app.route('/lines', methods=['GET'])
@app.route('/lines/<line>', methods=['GET'])
def lines(line=None):
    session.clear()
    gr = utils.get_graph(session, key='underground')

    data = []
    edges = gr.graph.edges(data=True)
    for edge in edges:
        if not line or line in edge[2]['line']:
            data.append({
                'source': edge[0],
                'target': edge[1],
                'line': edge[2]['line']
            })
    return jsonify(lines=data)


@app.route('/forced_layout', methods=['GET'])
def forced_layout():
    session.clear()
    gr = utils.get_graph(session, key='underground')
    all_stations = gr.station_data

    data = []
    stations = []
    edges = gr.graph.edges(data=True)
    for edge in edges:
        try:
            stations.append(all_stations[edge[0]])
            stations.append(all_stations[edge[1]])
        except:
            continue

        data.append({
            'source': edge[0],
            'target': edge[1],
            'line': edge[2]['line']
        })
    stations = dict((v['name'], v) for v in stations).values()
    id_stations = []
    for i, e in enumerate(stations):
        e['id'] = i
        id_stations.append(e)
    id_edges = []
    for edge in edges:
        station = filter(
            lambda station: station['name'] == edge[1],
            stations
        )
        if not station:
            continue
        dst = station[0]['id']
        station = filter(
            lambda station: station['name'] == edge[0],
            stations
        )
        if not station:
            continue
        src = station[0]['id']
        id_edges.append(
            {'source': src, 'target': dst, 'data': edge[2]}
        )
    return jsonify(stations=id_stations, lines=id_edges)


@app.route('/degree/<plot_type>/<network>')
def degree(plot_type=None, network='network'):
    if not plot_type:
        abort(404)
    if plot_type not in ['scatter', 'powerlaw']:
        abort(404)
    if network not in ['network', 'underground']:
        abort(404)

    gr = utils.get_graph(session, key=network)
    data = Counter(nx.degree(gr.graph).values())
    if plot_type == 'scatter':
        data = [
            {"x": int(k), "y": int(v)}
            for k, v in data.iteritems()
        ]
        return jsonify(scatter_points=data)
    elif plot_type == 'powerlaw':
        x, y = data.keys(), data.values()
        x = np.array(x)
        y = np.log(np.array(y))

        grad, inter = np.polyfit(np.log(x), y, 1)
        y = inter + (grad * np.log(x))

        data = [
            {"x": datum[0], "y": datum[1]}
            for datum in zip(x, np.exp(y))
        ]
        return jsonify(bestfit=data)
