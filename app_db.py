from device_db import DeviceDB

DB_NAME = 'data.db'


def get_db_handler():
    if not get_db_handler.handler:
        get_db_handler.handler = DeviceDB(DB_NAME)
    return get_db_handler.handler


get_db_handler.handler = None
