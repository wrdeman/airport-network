from flask import jsonify, render_template, request
from app import app, utils


@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html')


@app.route('/actor/<actor_id>')
def actor(actor_id):
    data = utils.get_actor(actor_id)
    return jsonify(**data)


@app.route('/search', methods=['GET'])
def search():
    if request.method == "GET":
        try:
            q = request.args.get('q')
        except KeyError:
            return []
        actors, movies = utils.search(q)
        actors.update(movies)
        return jsonify(actors)
    else:
        return []
