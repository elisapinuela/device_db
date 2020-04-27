from flask_restplus import Namespace, Resource
from device_db import DeviceDB

namespace_device = Namespace("device", description='Methods for device')
namespace_table = Namespace("table", description='Basic methods for tables')

HANDLER_DB = DeviceDB('data.db')


@namespace_device.route("/device")
@namespace_device.response(200, 'OK')
class Device(Resource):

    def get(self):
        return {"message": "This is a test"}, 200


resource_fields = namespace_table.model('Standard_Resource', {})


@namespace_table.route("/<string:table_name>")
@namespace_table.doc(params={'table_name': 'Table name for the request'})
@namespace_table.response(200, 'OK')
@namespace_table.response(404, 'BAD REQUEST')
class Table(Resource):

    def get(self, table_name):
        is_ok, data = HANDLER_DB.obtain_all(table_name)
        if not is_ok:
            return {'message': data}, 404
        return data, 200

    @namespace_table.doc(body=resource_fields)
    def post(self, table_name):
        is_ok, data = HANDLER_DB.registry(table_name)
        if not is_ok:
            return {'message': data}, 404
        return data, 200
