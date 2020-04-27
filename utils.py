from datetime import datetime, date
from sqlalchemy import *
from sqlalchemy import exc
from datetime import datetime


class Utils:

    @staticmethod
    def format_out_json(row_data):
        # Convert row data to dict
        row_dict = dict(row_data.items())
        # Look for date, datetime and None objects to format the JSON correctly
        for key, value in row_dict.items():
            replace_value = True
            new_value = []
            if isinstance(value, datetime):
                new_value = value.strftime("%d/%m/%Y, %H:%M:%S")
            elif isinstance(value, date):
                new_value = value.strftime("%d/%m/%Y")
            elif value is None:
                pass
            else:
                replace_value = False
            # Replace the value here
            if replace_value:
                row_dict[key] = new_value
        return row_dict

    @staticmethod
    def format_in_json(json_data, table_types):
        new_json = dict(json_data)
        for key, value in json_data.items():
            # Get the type
            if key == 'email':
                if type(value) is str:
                    value = value.lower()
                else:
                    for idx, val in enumerate(value):
                        new_json[key][idx] = val.lower()
            if key in table_types.keys():
                var_type = table_types[key]
                replace_value = True
                new_value = None
                if var_type == 'DATE':
                    if value:
                        new_value = datetime.strptime(value, "%d/%m/%Y")
                elif var_type == 'DATETIME':
                    if value:
                        new_value = datetime.strptime(value, "%d/%m/%Y, %H:%M:%S")
                elif var_type == 'INTEGER' or var_type == 'FLOAT' or var_type == 'BOOLEAN':
                    replace_value = False
                else:
                    if value:
                        replace_value = False
                # Replace the value here
                if replace_value:
                    new_json[key] = new_value
            else:
                print("Invalid key found in JSON body: %s" % key)
                return {}
        return new_json
