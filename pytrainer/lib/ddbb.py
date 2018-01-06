# -*- coding: iso-8859-1 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net
# vud1@grupoikusnet.com
# Jakinbidea & Grupo Ikusnet Developer
# Modified by dgranda

#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import logging
import os
import dateutil
from pytrainer.util.color import color_from_hex_string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator
from sqlalchemy import Integer, Table, Column, ForeignKey

DeclarativeBase = declarative_base()

record_to_equipment = Table('record_equipment', DeclarativeBase.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('equipment_id', Integer,
                                   ForeignKey('equipment.id'),
                                   index=True, nullable=False),
                            Column('record_id', Integer,
                                   ForeignKey('records.id_record'),
                                   index=True, nullable=False))

#Define the tables and their columns that should be in the database
#Obviously, this is not a list but a dict -> TODO: ammend name to avoid confusion!!!
tablesList = {  "records":{     "id_record":"integer primary key autoincrement",
                                        "date":"date",
                                        "sport":"integer",
                                        "distance":"float",
                                        "time":"varchar(200)",
                                        "duration": "integer",
                                        "beats":"float",
                                        "average":"float",
                                        "calories":"int",
                                        "comments":"text",
                                        "gpslog":"varchar(200)",
                                        "title":"varchar(200)",
                                        "upositive":"float",
                                        "unegative":"float",
                                        "maxspeed":"float",
                                        "maxpace":"float",
                                        "pace":"float",
                                        "maxbeats":"float",
                                        "date_time_local":"varchar(40)",
                                        "date_time_utc":"varchar(40)",
                                        },
                        "sports":{      "id_sports":"integer primary key autoincrement",
                                        "name":"varchar(100)",
                                        "weight":"float",
                                        "met":"float",
                                        "max_pace":"integer",
                                        "color":"char(6)",
                                        },
                        "waypoints":{   "id_waypoint":"integer primary key autoincrement",
                                        "lat":"float",
                                        "lon":"float",
                                        "ele":"float",
                                        "comment":"varchar(240)",
                                        "time":"date",
                                        "name":"varchar(200)",
                                        "sym":"varchar(200)",
                                        },
                        "laps":{        "id_lap": "integer primary key autoincrement",
                                        "record": "integer",
                                        "lap_number": "integer",
                                        "elapsed_time": "varchar(20)",
                                        "distance": "float",
                                        "start_lat": "float",
                                        "start_lon": "float",
                                        "end_lat": "float",
                                        "end_lon": "float",
                                        "calories": "int",
                                        "intensity": "varchar(7)",
                                        "laptrigger": "varchar(9)",
                                        "max_speed": "float",
                                        "avg_hr": "int",
                                        "max_hr": "int",
                                        "comments":"text",
                                        },
                        "athletestats": {
                                        "id_athletestat": "integer primary key autoincrement",
                                        "date": "date",
                                        "weight": "float",
                                        "bodyfat": "float",
                                        "restinghr": "integer",
                                        "maxhr": "integer",
                                        },
                        "equipment": {
                                      "id": "integer primary key autoincrement" ,
                                      "description": "varchar (200)",
                                      "active": "boolean",
                                      "life_expectancy": "int",
                                      "prior_usage": "int",
                                      "notes": "text",
                                      },
                        "record_equipment": {
                                     "id": "integer primary key autoincrement",
                                     "record_id": "int",
                                     "equipment_id": "int",
                                     }
                        }

class DDBB:
    def __init__(self, url=None):
        """Initialize database connection, defaulting to SQLite in-memory
if no url is provided"""
        if url:
            self.url = url
        else:
            if 'PYTRAINER_ALCHEMYURL' in os.environ:
                self.url = os.environ['PYTRAINER_ALCHEMYURL']
            else:
                self.url = "sqlite://"
        if self.url.startswith("sqlite"):
            from sqliteUtils import Sql
        elif self.url.startswith("mysql"):
            from mysqlUtils import Sql
        self.engine = create_engine(self.url, logging_name='db')
        self.ddbbObject = Sql()
        logging.info("DDBB created with url %s", self.url)

    def get_connection_url(self):
        return self.url

    def connect(self):
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.ddbbObject.connect(self.engine.raw_connection())

    def disconnect(self):
        self.session.close()
        self.ddbbObject.disconnect()
        self.engine.dispose()

    def select(self,table,cells,condition=None, mod=None):
        logging.warning("Deprecated call to ddbb.select")
        sql = "select %s from %s" %(cells,table)
        if condition is not None:
            sql = "%s where %s" % (sql, condition)
        if mod is not None:
            sql = "%s %s" % (sql, mod)
        return list(self.session.execute(sql))

    def select_dict(self,table,cells,condition=None, mod=None):
        '''
        Function to query DB
        -- inputs
        ---- table - string tablename(s)
        ---- cells - list of cells to select
        ---- condition - string to fit SQL where clause or None
        ---- mod - string of select clause modifier, eg "order by date"
        -- returns
        ---- list of dicts with cells as keys
        '''
        logging.debug(">>")
        global tablesList
        return_value = []
        #Only query db if table and cells are supplied
        if table is not None and cells is not None:
            if table.find(',') != -1:
                #multiple tables in select
                #TODO fix so works....
                logging.info('TODO fix select_dict to work with multiple tables')
                cellString = ','.join(cells) #create cell list string
                results = self.select(table,cellString,condition,mod)
                for result in results:
                    dict = {}
                    #Loop through cells and create dict of results
                    for i, cell in enumerate(cells):
                        #cell_type = tablesList[table][cell]
                        dict[cell] = result[i]
                    return_value.append(dict)
            elif table in tablesList:
                cellString = ','.join(cells) #create cell list string
                results = self.select(table,cellString,condition,mod)
                for result in results:
                    dict = {}
                    #Loop through cells and create dict of results
                    for i, cell in enumerate(cells):
                        #check result is correct type
                        if cell not in tablesList[table]:
                            logging.error('select includes invalid cell (%s) for table %s' % (cell, table))
                        else:
                            cell_type = tablesList[table][cell]
                            dict[cell] = self.parseByCellType(result[i], cell_type)
                    return_value.append(dict)
            else:
                logging.error('select on invalid table name')
        logging.debug("<<")
        return return_value

    def parseByCellType(self, value, cell_type):
        '''
        Function to validate that value is of type cell_type
        '''
        #TODO need to check if multivalue cell type specified
        # eg integer primary key autoincrement
        #print "Checking if %s is of type %s" % (value, cell_type)
        if cell_type.startswith('float'):
            try:
                result = float(value)
                return result
            except Exception as e:
                #print "%s not float" % value
                return None
        elif cell_type.startswith('int'):
            try:
                result = int(value)
                return result
            except Exception as e:
                #print "%s not int" % value
                return None
        elif cell_type.startswith('text'):
            #Text so is OK??
            #TODO anytests required here??
            return value
        elif cell_type.startswith('varchar'):
            #Text so is OK??
            #TODO check length against spec?
            return value
        elif cell_type.startswith('char'):
            #Text so is OK??
            #TODO check length against spec?
            return value
        elif cell_type.startswith('date'):
            try:
                result = dateutil.parser.parse(value).date()
                return result
            except Exception as e:
                #print type(e)
                #print e
                #print "%s not date" % value
                return None
        print "Unknown datatype: (%s) for data (%s)" % (cell_type, value)
        return None

    def insert(self,table,cells,values):
        self.ddbbObject.insert(table,cells,values)

    def insert_dict(self, table, data):
        logging.debug(">>")
        global tablesList
        if not table or not data or table not in tablesList:
            print "insert_dict called with invalid table or no data"
            logging.debug("!<<")
            return False
        cells = []
        values = []
        for cell in data:
            cell_type = tablesList[table][cell]
            cell_value = self.parseByCellType(data[cell], cell_type)
            if cell_value is not None:
                cells.append(cell)
                values.append(cell_value)
        #Create string of cell names for sql...
        #TODO fix sql objects so dont need to join...
        cells_string = ",".join(cells)
        self.ddbbObject.insert(table,cells_string,values)
        logging.debug("<<")

    def delete(self,table,condition):
        self.ddbbObject.delete(table,condition)

    def update(self,table,cells,value,condition):
        self.ddbbObject.update(table,cells,value,condition)

    def update_dict(self, table, data, condition):
        logging.debug(">>")
        global tablesList
        if not table or not data or table not in tablesList:
            print "update_dict called with invalid table or no data"
            logging.debug("!<<")
            return False
        cells = []
        values = []
        for cell in data:
            cell_type = tablesList[table][cell]
            cell_value = self.parseByCellType(data[cell], cell_type)
            if cell_value is not None:
                cells.append(cell)
                values.append(cell_value)
        #Create string of cell names for sql...
        #TODO fix sql objects so dont need to join...
        cells_string = ",".join(cells)
        self.ddbbObject.update(table,cells_string,values,condition)
        logging.debug("<<")

    def lastRecord(self,table):
        id = "id_" + table[:-1] #prune 's' of table name and pre-pend 'id_' to get id column
        sql = "select %s from %s order by %s Desc limit 0,1" %(id,table,id)
        ret_val = self.ddbbObject.freeExec(sql)
        return ret_val[0][0]
        
    def create_tables(self, add_default=True):
        """Initialise the database schema from an empty database."""
        logging.info("Creating database tables")
        from pytrainer.core.sport import Sport
        from pytrainer.core.equipment import Equipment
        from pytrainer.waypoint import Waypoint
        from pytrainer.core.activity import Lap
        from pytrainer.athlete import Athletestat
        DeclarativeBase.metadata.create_all(self.engine)
        if add_default:
            for item in [Sport(name=u"Mountain Bike", weight=0.0, color=color_from_hex_string("0000ff")),
                         Sport(name=u"Bike", weight=0.0, color=color_from_hex_string("00ff00")),
                         Sport(name=u"Run", weight=0.0, color=color_from_hex_string("ffff00"))]:
                self.session.add(item)
            self.session.commit()

    def drop_tables(self):
        """Drop the database schema"""
        DeclarativeBase.metadata.drop_all(self.engine)
                
    def create_backup(self):
        """Create a backup of the current database."""
        import urlparse
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(self.url)
        if scheme == 'sqlite':
            import urllib
            import datetime
            import gzip
            logging.info("Creating compressed copy of current DB")
            logging.debug('Database path: %s', self.url)
            path = urllib.url2pathname(path)
            backup_path = '%s_%s.gz' % (path, datetime.datetime.now().strftime('%Y%m%d_%H%M'))
            with open(path, 'rb') as orig_file:
                with gzip.open(backup_path, 'wb') as backup_file:
                    backup_file.write(orig_file.read())
                    logging.info('Database backup successfully created')

class ForcedInteger(TypeDecorator):
    """Type to force values to int since sqlite doesn't do this"""
    impl = Integer

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        else:
            return int(value)
