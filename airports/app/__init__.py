from flask import Flask
from flask.ext.navigation import Navigation

app = Flask(__name__)
nav = Navigation(app)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
from app import views
