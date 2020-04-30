import flask
from flask import request, render_template, make_response
from flask_cors import CORS
from flask_restplus import Api
from device_api import namespace_device
from basic_api import ns_db
import os


# This allows us to use a plain HTTP callback
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = flask.Flask(__name__)
CORS(app)
api = Api(app, version='1.0', title='Device Library', description='Database server for Device Library')
app.secret_key = os.urandom(24)
app.config['CORS_HEADERS'] = 'Content-Type'

api.add_namespace(namespace_device)
api.add_namespace(ns_db)


if __name__ == "__main__":
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='127.0.0.1', port=5000, debug=True, ssl_context=('cert.pem', 'key.pem'), use_reloader=False)
