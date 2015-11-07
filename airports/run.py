#!/home/vagrant/venv/site/bin/python
from app import app
from session import session_setup

if __name__ == "__main__":
    app = session_setup(app)
    app.config.from_object('config.DevelopmentConfig')
    app.run(host='0.0.0.0', port=8000)
