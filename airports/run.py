#!/home/vagrant/venv/site/bin/python
from flask.sessions import SessionInterface
from werkzeug.contrib.fixers import ProxyFix
from beaker.middleware import SessionMiddleware

from app import app

session_opts = {
    'session.type': 'ext:memcached',
    'session.url': '127.0.0.1:11211',
    'session.data_dir': './cache',
    }


class BeakerSessionInterface(SessionInterface):
    def open_session(self, app, request):
        session = request.environ['beaker.session']
        return session

    def save_session(self, app, session, response):
        session.save()


app.wsgi_app = ProxyFix(app.wsgi_app)
app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)
app.session_interface = BeakerSessionInterface()

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8000)
