#!/home/vagrant/venv/site/bin/python
from app import app
from session import session_setup
from wdb.ext import WdbMiddleware

app.wsgi_app = WdbMiddleware(app.wsgi_app)
app = session_setup(app)
app.config.from_object('config.DevelopmentConfig')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, use_debugger=False)
