from flask import request
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



