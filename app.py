import flask
from flask import request, render_template, make_response
from flask_cors import CORS
from flask_restplus import Api
from device_api import namespace_device, namespace_table
import os


# This allows us to use a plain HTTP callback
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = flask.Flask(__name__)
CORS(app)
api = Api(app, version='1.0', title='Device Library', description='Database server for Device Library')
app.secret_key = os.urandom(24)
app.config['CORS_HEADERS'] = 'Content-Type'

api.add_namespace(namespace_device)
api.add_namespace(namespace_table)




# @namespace_user.route('/data')
# class Test(Resource):
#     @api.response(404, 'BAD_REQUEST')
#     @api.response(200, 'OK')
#     @api.doc(body=request_fields)
#     def post(self):
#         body = request.json
#         try:
#             HANDLER_DB.engine.execute(HANDLER_DB.table.insert(), dato1=body['data'])
#         except Exception as Error:
#             return {'message': str(Error)}, 404
#         return {'message': 'Dato insertado correctamente [%d].' % (body['data'])}, 200
#
#     @api.response(200, 'OK')
#     def get(self):
#         data = HANDLER_DB.getdata()
#         return {'message': 'Acceso a los datos correcto', 'datos': data}, 200
#
#     @api.response(200, 'OK')
#     def delete(self):
#         if HANDLER_DB.erasedata():
#             return {'message': 'Datos borrados correctamente'}, 200
#         else:
#             return {'message': 'Error al borrar los datos'}, 404
#
#
# @namespace_user.route('/initdb')
# class Init(Resource):
#     @api.response(200, 'OK')
#     def get(self):
#         try:
#             HANDLER_DB.engine.execute(HANDLER_DB.table.insert(), dato1=12)
#         except Exception as Error:
#             return {'message': str(Error)}, 400
#         return {'message': 'Base de datos inicializada correctamente.'}, 200
#
#
# @namespace_user.route('/dashboard')
# class Dashboard(Resource):
#     def get(self):
#         headers = {'Content-Type': 'text/html'}
#         return make_response(render_template('dashboard.html'), 200, headers)


if __name__ == "__main__":
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='127.0.0.1', port=5000, debug=True, ssl_context=('cert.pem', 'key.pem'), use_reloader=False)
