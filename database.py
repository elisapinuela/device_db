from sqlalchemy import *
from sqlalchemy import exc
from datetime import datetime, date


class DataBase:

    def __init__(self, metadata, db_engine):
        self.metadata = metadata
        self.engine = db_engine
        if self.engine.url.drivername != 'mysql':
            self.isMySql = False
        else:
            self.isMySql = True
        self.__connection = None
        self.__init_types()

    def __init_types(self):
        # Create the types and add tracking attribute for each table
        for table_object in self.metadata.tables.values():
            table_object.types = {}
            for col in table_object.columns:
                table_object.types[str(col.name)] = str(col.type)
            if 'created_at' in table_object.columns:
                table_object.tracking = True
            else:
                table_object.tracking = False

    def tree(self):
        # Build a JSON tree of database structure
        table_list = {}
        for table_name, table_obj in self.metadata.tables.items():
            column_list = {}
            # table_item = {table_name: []}
            for column_name, column_object in table_obj.columns.items():
                column_list.update({column_name: str(column_object.type)})
            table_list.update({table_name: column_list})
        return True, {"message": "DB tree data obtained OK", "db_tree": table_list}

    def obtain(self, table_name, table_id, obtain_deleted=False):
        try:
            table_object = self.metadata.tables[table_name]
        except KeyError:
            return False, "Table required %s not found" % table_name

        query = select([table_object]).where(table_object.columns.id == table_id)
        is_ok, result = self.connection_execute(query, fetchall=True)
        if not is_ok:
            return False, result
        if not len(result):
            return False, "%s ID %d not found in the DB" % (table_object.name, table_id)
        if len(result) > 1:
            return False, "Unexpected error, %s ID is not unique in the DB" % table_name
        new_dict = self.format_out_json(result[0])
        # Check if user has been deleted
        if not obtain_deleted and table_object.tracking and new_dict["deleted_at"]:
            return False, "%s with ID %d has been deleted from the DB" % (table_name, table_id)
        return True, {"message": "%s obtained OK" % table_name, table_name: new_dict}

    def modify(self, table_name, table_id, data, obtain_deleted=False):
        try:
            table_object = self.metadata.tables[table_name]
        except KeyError:
            return False, "Table required '%s' not found" % table_name

        new_data = self.format_in_json(data, table_object.types)
        if not new_data:
            return False, "Invalid JSON body format"
        # Add updating date
        if table_object.tracking:
            new_data["updated_at"] = datetime.now()

        is_ok, result = self.connection_execute(table_object.update().where(table_object.columns.id == table_id),
                                                new_data)
        if not is_ok:
            return False, result
        if not result.rowcount:
            return False, "Id %d not found in %s table" % (table_id, table_name)
        # Get the new data of modified ID
        is_ok, data = self.obtain(table_name, table_id, obtain_deleted)
        if is_ok:
            return True, {"message": "%s modified OK" % table_name, table_name: data[table_name]}
        else:
            return False, data

    def registry(self, table_name, data):
        try:
            table_object = self.metadata.tables[table_name]
        except KeyError:
            return False, "Table required '%s' not found" % table_name

        new_data = self.format_in_json(data, table_object.types)
        if not new_data:
            return False, "Invalid JSON body format"
        # Add creation date
        if table_object.tracking:
            new_data["created_at"] = datetime.now()
            new_data["updated_at"] = datetime.now()

        is_ok, result = self.connection_execute(table_object.insert(), new_data)
        if not is_ok:
            return False, result

        if not result.rowcount:
            return False, "Error while registering new %s" % table_name
        # Get the id of inserted row
        inserted_id = result.inserted_primary_key[0]
        # Get the data of this ID
        is_ok, data = self.obtain(table_name, inserted_id)
        if is_ok:
            return True, {"message": "%s registered OK" % table_name, table_name: data[table_name]}
        else:
            return False, data

    def remove(self, table_name, table_id):
        try:
            table_object = self.metadata.tables[table_name]
        except KeyError:
            return False, "Table required '%s' not found" % table_name

        if table_object.tracking:
            # Get the row with this id
            is_ok, data = self.obtain(table_name, table_id, True)
            if is_ok:
                # Check if item has been already deleted
                if data[table_name]["deleted_at"]:
                    return False, "%s with ID %d has been already deleted" % (table_name, table_id)
                else:
                    now = datetime.now()
                    new_data = {"deleted_at": datetime.strftime(now, "%d/%m/%Y, %H:%M:%S")}
                    is_ok, data = self.modify(table_name, table_id, new_data, True)
                    if is_ok:
                        return is_ok, {"message": "%s with ID %d deleted OK" % (table_name, table_id)}
                    else:
                        return False, data
            else:
                return False, data
        else:
            is_ok, result = self.connection_execute(table_object.delete().where(table_object.columns.id == table_id))
            if not is_ok:
                return False, result
            if not result.rowcount:
                return False, "Error while deleting %s with ID %d" % (table_name, table_id)
            return True, {"message": "%s with ID %d deleted OK" % (table_name, table_id)}

    def remove_all(self, table_name, hard=False):
        try:
            table_object = self.metadata.tables[table_name]
        except KeyError:
            return False, "Table required '%s' not found" % table_name

        if table_object.tracking and not hard:
            # Get the row with this id
            is_ok, data = self.obtain_all(table_name, obtain_deleted=True)
            if is_ok:
                deleted_items = 0
                not_deleted_items = 0
                for item in data[table_name]:
                    # Check if item has been already deleted
                    if not item["deleted_at"]:
                        not_deleted_items += 1
                        now = datetime.now()
                        new_data = {"deleted_at": datetime.strftime(now, "%d/%m/%Y, %H:%M:%S")}
                        is_ok, data = self.modify(table_name, item['id'], new_data, True)
                        if is_ok:
                            deleted_items += 1
                return True, {"message": "%d of %d deleted" % (deleted_items, not_deleted_items)}
            else:
                return False, data
        else:
            is_ok, result = self.connection_execute(table_object.delete())
            if not is_ok:
                return False, result
            if not result.rowcount:
                return False, "Error while deleting %s table records" % table_name
            return True, {"message": "%s table records deleted OK" % table_name}

    def obtain_all(self, table_name, obtain_deleted=False):
        try:
            table_object = self.metadata.tables[table_name]
        except KeyError:
            return False, "Table required %s not found" % table_name

        query = select([table_object])
        is_ok, result = self.connection_execute(query,  fetchall=True)
        if not is_ok:
            return False, result

        if not len(result):
            return False, "No items found in the table %s for the DB" % table_name
        item_list = []
        for row in result:
            row_json = self.format_out_json(row)
            if not obtain_deleted:
                # Do not return deleted items
                if table_object.tracking and row_json["deleted_at"]:
                    continue
            item_list.append(row_json)
        return True, {"message": "%s obtained OK" % table_name, table_name: item_list}

    def obtain_filtered(self, table_name, filter_name, filter_list):
        try:
            table_object = self.metadata.tables[table_name]
        except KeyError:
            return False, "Table required %s not found" % table_name
        try:
            column_object = table_object.columns[filter_name]
        except KeyError:
            return False, "Column required %s for the Table %s not found" % (filter_name, table_name)
        query = select([table_object]).where(column_object.in_(filter_list))
        is_ok, result = self.connection_execute(query,  fetchall=True)
        if not is_ok:
            return False, result
        if not len(result):
            return False, "No items found in the table €s for the DB" % table_name
        item_list = []
        for row in result:
            row_json = self.format_out_json(row)
            # Do not return deleted items
            if table_object.tracking and row_json["deleted_at"]:
                continue
            item_list.append(row_json)
        return True, {"message": "%s obtained OK" % table_name, table_name: item_list}

    def get_db(self):
        table_object = list(self.metadata.tables.keys())
        data_all = {}
        data_table = []
        for table_item in table_object:
            query = select([self.metadata.tables[table_item]]) \
                .where(self.metadata.tables[table_item].columns.id != 0)
            is_ok, result = self.connection_execute(query, fetchall=True)
            if not is_ok:
                return False, result
            for data_item in result:
                data_table.append(self.format_out_json(data_item))
            data_all[table_item] = data_table
            data_table = []
        return True, data_all

    def _drop_db(self):
        try:
            self.metadata.drop_all(bind=self.engine)
        except exc.SQLAlchemyError as Error:
            return False, Error.__str__()
        return True, {"message": "All tables have been dropped successfully."}

    def restart_engine(self):
        self._drop_db()
        self.metadata.create_all(self.engine)
        return True, {"message": "DB restarted OK"}

    def db_init_from_json(self, data):
        # Restart the db before loading new data (drop all tables)
        self.restart_engine()
        json_data = data
        db_tables = self.metadata.sorted_tables
        for table_obj in db_tables:
            # Check if table name is from user or company db
            if table_obj.name in json_data.keys():
                insert_data = True
            else:
                print("Table  %s is missing in JSON file, not initialized" % table_obj.name)
                insert_data = False

            if insert_data:
                for item in json_data[table_obj.name]:
                    # Format input JSOn
                    input_json = self.format_in_json(item, table_obj.types)
                    if table_obj.tracking:
                        input_json["created_at"] = datetime.now()
                        input_json["updated_at"] = datetime.now()
                    is_ok, result = self.connection_execute(table_obj.insert(), input_json)
                    if not is_ok:
                        return False, result
               
        return True, {"message": "The database has been filled successfully."}

    def connect_engine(self):
        if not self.__connection:
            try:
                self.__connection = self.engine.connect()
            except exc.SQLAlchemyError as Error:
                raise Error
        else:
            # Do nothing, connection already open
            pass

    def disconnect_engine(self):
        self.__connection.close()
        self.__connection = None

    def connection_execute(self, query, data=None, disconnect=True, fetchall=False):
        is_ok, result = True, None
        if not self.__connection:
            self.connect_engine()
        try:
            if data:
                result = self.__connection.execute(query, data)
            else:
                result = self.__connection.execute(query)
        except exc.SQLAlchemyError as Error:
            is_ok = False
            result = Error.__str__()
        if is_ok and fetchall:
            result = result.fetchall()
        if disconnect:
            self.disconnect_engine()
        return is_ok, result

    def is_connection_open(self):
        if self.__connection:
            return True
        else:
            return False
    
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
