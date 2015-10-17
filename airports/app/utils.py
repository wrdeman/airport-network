from flask import g

from py2neo import authenticate, Graph


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'graph_db'):
        authenticate("localhost:7474", "neo4j", "0000")
        g.graph_db = Graph()
        return g.graph_db


def get_actor(actor_id):
    """ returns name, biography and films associated to actor

    input: actor_id
    """
    graph = get_db()
    if isinstance(actor_id, int):
        try:
            actor_id = str(int)
        except ValueError:
            raise Exception
    node = graph.find_one('Actor', 'id', actor_id)
    if not node:
        raise Exception

    ctx = {}
    properties = node.get_properties()
    films = []
    if properties:
        for film in graph.match(start_node=node, rel_type='ACTS_IN'):
            film_props = film.end_node.get_properties()
            films.append(
                {'title': film_props['title'],
                 'film_id': film_props['id']}
            )

        ctx.update(
            {
                'name': properties['name'],
                'bio': properties['biography'],
                'films': films,
            }
        )

    return ctx


def search(q, actor=True, movie=True):
    """ search all actors/movies
    return dict actors, movies

    actors = {"actors": [{"name": name, "id": id}]

    kwargs:
    actor/movie True, False to search for either category
    """
    graph = get_db()
    actors, movies = {}, {}
    if actor:
        query = ("MATCH (actor:Actor) "
                 "WHERE actor.name =~ '(?i).*"+q+".*' "
                 "RETURN actor")
        results = graph.cypher.execute(query)
        actors = {
            'actors': [
                {'name': row.actor['name'], 'id': row.actor['id']}
                for row in results
            ]
        }
    if movie:
        query = ("MATCH (movie:Movie) "
                 "WHERE movie.title =~ '(?i).*"+q+".*' "
                 "RETURN movie")
        results = graph.cypher.execute(query)
        movies = {
            'movies': [
                {'title': row.movie['title'], 'id': row.movie['id']}
                for row in results
            ]
        }

    return actors, movies
