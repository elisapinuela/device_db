from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey
from sqlalchemy import Integer, String, DateTime
from database import DataBase


class DeviceDB(DataBase):

    def __init__(self, db_path):
        engine_name = "sqlite:///" + db_path
        self.engine = create_engine(engine_name, echo=True)
        self.metadata = MetaData(bind=None)
        # Categories
        self.categories = Table('categories', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('name', String, nullable=False),
                                Column('parent', String, nullable=True),
                                Column('created_at', DateTime, nullable=False),
                                Column('updated_at', DateTime, nullable=True),
                                Column('deleted_at', DateTime))

        # Locations
        self.locations = Table('locations', self.metadata,
                               Column('id', Integer, primary_key=True),
                               Column('name', String, nullable=False),
                               Column('details', String, nullable=True),
                               Column('created_at', DateTime, nullable=False),
                               Column('updated_at', DateTime, nullable=True),
                               Column('deleted_at', DateTime))

        # Tags
        self.tags = Table('tags', self.metadata,
                          Column('id', Integer, primary_key=True),
                          Column('name', String, nullable=False),
                          Column('created_at', DateTime, nullable=False),
                          Column('updated_at', DateTime, nullable=True),
                          Column('deleted_at', DateTime))

        # Devices
        self.devices = Table('devices', self.metadata,
                             Column('id', Integer, primary_key=True),
                             Column('name', String, nullable=False),
                             Column('description', String, nullable=True),
                             Column('image_url', String),
                             Column('datasheet_url', String),
                             Column('location_id', Integer,
                                    ForeignKey('locations.id')),
                             Column('created_at', DateTime, nullable=False),
                             Column('updated_at', DateTime, nullable=True),
                             Column('deleted_at', DateTime))

        # Devices_categories
        self.devices_categories = Table('devices_categories', self.metadata,
                                        Column('id', Integer, primary_key=True),
                                        Column('device_id', Integer, ForeignKey('devices.id')),
                                        Column('category_id', Integer, ForeignKey('categories.id')))

        # Devices_tags
        self.devices_tags = Table('devices_tags', self.metadata,
                                  Column('id', Integer, primary_key=True),
                                  Column('device_id', Integer, ForeignKey('devices.id')),
                                  Column('tag_id', Integer, ForeignKey('tags.id')))

        self.metadata.create_all(self.engine)
        # Init base class data
        DataBase.__init__(self, self.metadata, self.engine)

