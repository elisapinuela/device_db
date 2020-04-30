from flask import request
from flask_restplus import Namespace, Resource
from app_db import get_db_handler

ns_db = Namespace("db", description='Basic methods for tables')

empty_body = ns_db.model('Standard_Resource', {})

HANDLER_DB = get_db_handler()


@ns_db.route("/init")
@ns_db.response(200, 'OK')
@ns_db.response(404, 'BAD REQUEST')
class Restart(Resource):
    @ns_db.doc(body=empty_body)
    def post(self):
        body_data = request.json
        is_ok, data = HANDLER_DB.db_init_from_json(body_data)
        if not is_ok:
            return {'message': data}, 404
        return data, 200


@ns_db.route("/restart")
@ns_db.response(200, 'OK')
@ns_db.response(404, 'BAD REQUEST')
class Restart(Resource):
    def post(self):
        is_ok, data = HANDLER_DB.restart_engine()
        if not is_ok:
            return {'message': data}, 404
        return data, 200


@ns_db.route("")
@ns_db.response(200, 'OK')
@ns_db.response(404, 'BAD REQUEST')
class GetDB(Resource):
    def get(self):
        is_ok, data = HANDLER_DB.get_db()
        if not is_ok:
            return {'message': data}, 404
        return data, 200


@ns_db.route("/tree")
@ns_db.response(200, 'OK')
@ns_db.response(404, 'BAD REQUEST')
class Tree(Resource):
    def get(self):
        is_ok, data = HANDLER_DB.tree()
        if not is_ok:
            return {'message': data}, 404
        return data, 200


@ns_db.route("/table/<string:table_name>/all")
@ns_db.doc(params={'table_name': 'Table name for the request'})
@ns_db.response(200, 'OK')
@ns_db.response(404, 'BAD REQUEST')
class TableAll(Resource):
    def get(self, table_name):
        is_ok, data = HANDLER_DB.obtain_all(table_name)
        if not is_ok:
            return {'message': data}, 404
        return data, 200

    def delete(self, table_name):
        is_ok, data = HANDLER_DB.remove_all(table_name, hard=True)
        if not is_ok:
            return {'message': data}, 404
        return data, 200


@ns_db.route("/table/<string:table_name>")
@ns_db.doc(params={'table_name': 'Table name for the request'})
@ns_db.response(200, 'OK')
@ns_db.response(404, 'BAD REQUEST')
class TableRegistry(Resource):
    @ns_db.doc(body=empty_body)
    def post(self, table_name):
        body_data = request.json
        is_ok, data = HANDLER_DB.registry(table_name, body_data)
        if not is_ok:
            return {'message': data}, 404
        return data, 200


@ns_db.route("/table/<string:table_name>/<int:table_id>")
@ns_db.doc(params={'table_name': 'Table name for the request', 'table_id': 'Table id for the request'})
@ns_db.response(200, 'OK')
@ns_db.response(404, 'BAD REQUEST')
class TableById(Resource):
    def get(self, table_name, table_id):
        is_ok, data = HANDLER_DB.obtain(table_name, table_id)
        if not is_ok:
            return {'message': data}, 404
        return data, 200

    def delete(self, table_name, table_id):
        is_ok, data = HANDLER_DB.remove(table_name, table_id)
        if not is_ok:
            return {'message': data}, 404
        return data, 200

    @ns_db.doc(body=empty_body)
    def post(self, table_name, table_id):
        body_data = request.json
        is_ok, data = HANDLER_DB.modify(table_name, table_id, body_data)
        if not is_ok:
            return {'message': data}, 404
        return data, 200
