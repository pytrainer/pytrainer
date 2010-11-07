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
import traceback
import commands, os
import dateutil
from pytrainer.lib.date import Date

#Define the tables and their columns that should be in the database
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
tablesDefaultData = {  "sports": [({ "name":"Mountain Bike" } ), ( {"name": "Bike"}), ({"name": "Run"}) ]}


class DDBB:
    def __init__(self, configuration, pytrainer_main=None):
        self.pytrainer_main = pytrainer_main
        self.configuration = configuration
        self.ddbb_type = self.configuration.getValue("pytraining","prf_ddbb")
        if self.ddbb_type == "mysql": #TODO no longer supported?
            from mysqlUtils import Sql
        else:
            from sqliteUtils import Sql

        self.confdir = self.configuration.confdir
        self.ddbb_path = "%s/pytrainer.ddbb" %self.confdir

        ddbb_host = self.configuration.getValue("pytraining","prf_ddbbhost")
        ddbb = self.configuration.getValue("pytraining","prf_ddbbname")
        ddbb_user = self.configuration.getValue("pytraining","prf_ddbbuser")
        ddbb_pass = self.configuration.getValue("pytraining","prf_ddbbpass")
        self.ddbbObject = Sql(ddbb_host,ddbb,ddbb_user,ddbb_pass,self.configuration)

    def connect(self):
        connection_ok, connection_msg = self.ddbbObject.connect()
        if not connection_ok:
			print "ERROR: Unable to connect to database"
			print connection_msg
			sys.exit(connection_ok)
        #Do a quick check to ensure all tables are present in DB
        if not self.checkDBTables():
            #Some tables missing - do DB check
            self.checkDBIntegrity()

    def disconnect(self):
        self.ddbbObject.disconnect()

    def build_ddbb(self): #TODO Is this needed?
        self.ddbbObject.createDDBB()
        self.ddbbObject.connect()
        self.ddbbObject.createTables()
        self.ddbbObject.createTableVersion()

    def select(self,table,cells,condition=None, mod=None):
        return self.ddbbObject.select(table,cells,condition,mod)

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
                print 'TODO fix select_dict to work with multiple tables'
                cellString = ','.join(cells) #create cell list string
                results = self.ddbbObject.select(table,cellString,condition,mod)
                for result in results:
                    dict = {}
                    #Loop through cells and create dict of results
                    for i, cell in enumerate(cells):
                        #cell_type = tablesList[table][cell]
                        dict[cell] = result[i]
                    return_value.append(dict)
            elif table in tablesList:
                cellString = ','.join(cells) #create cell list string
                results = self.ddbbObject.select(table,cellString,condition,mod)
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
        
    def checkDBTables(self):
        '''Quick check that all expected tables existing in DB
            return True if OK, False if any tables are missing
        '''
        global tablesList
        logging.debug('>>')
        tablesDB = self.ddbbObject.getTableList()
        #Check Tables
        for entry in tablesList:
            if entry not in tablesDB:
                return False
        return True

    def checkDBIntegrity(self):
        '''17.11.2009 - dgranda
        Retrieves tables and columns from database, checks current ones and adds something if missed. New in version 1.7.0
        args: none
        returns: none'''
        global tablesList
        global tablesDefaultData
        logging.debug('>>')
        logging.info('Checking PyTrainer database')
        #if self.ddbb_type != "sqlite":
        #    logging.error('Support for MySQL database is decommissioned, please migrate to SQLite. Exiting check')
        #    exit(-2)
        try:
            tablesDBT = self.ddbbObject.getTableList()
        except:
            logging.error('Not able to retrieve which tables are in DB. Printing traceback')
            traceback.print_exc()
            exit(-1)

        tablesDB = [] # Database retrieves a list with tuples ¿?
        for entry in tablesDBT:
            tablesDB.append(entry[0])
        logging.debug('Found '+ str(len(tablesDB))+' tables in DB: '+ str(tablesDB))

        # Create a compressed copy of current DB
        try:
            self.ddbbObject.createDatabaseBackup()
        except:
            logging.error('Not able to make a copy of current DB. Printing traceback and exiting')
            traceback.print_exc()
            exit(-1)

        #Check Tables
        for entry in tablesList:
            if entry not in tablesDB:
                logging.warn('Table '+str(entry)+' does not exist in DB')
                self.ddbbObject.createTableDefault(entry,tablesList[entry])
                #Check if this table has default data to add..
                if entry in tablesDefaultData:
                    logging.debug("Adding default data to %s" % entry)
                    for data_dict in tablesDefaultData[entry]:
                        self.insert_dict(entry, data_dict)
            else:
                self.ddbbObject.checkTable(entry,tablesList[entry])

        #Run any functions to update or correct data
        #These functions _must_ be safe to run at any time (i.e. not be version specfic or only safe to run once)
        self.populate_date_time_local()
        self.populate_duration_from_time()
        logging.debug('<<')

    def checkDBDataValues(self):
        ''' Check all data in DB and report values that do not match the type '''
        global tablesList

        for table in tablesList.keys():
            pass

    def populate_duration_from_time(self):
        '''
        Populate duration from time field
            only for empty durations and where time can be parsed as an int
        '''
        logging.debug('--')
        listOfRecords = self.select_dict("records",('id_record','time'), "duration is NULL")
        logging.debug("Found %d records in DB without date_time_local field populated" % (len(listOfRecords) ) )
        for record in listOfRecords:
            try:
                duration = int(record['time'])
            except Exception as e:
                logging.info( "Error parsing time (%s) as int for record_id: %s" % (record['time'], record['id_record']))
                continue
            logging.debug("setting record %s duration to %d" % (record['id_record'], duration))
            data = {'duration': duration}
            self.update_dict("records",data ,"id_record = %d"%record['id_record'])

    def populate_date_time_local(self):
        ''' Populate date_time_local and date from date_time_utc
                only access records that date_time_local is NULL
                using OS timezone to create local_time

                also updates date if date != local_time

                TODO - leaves date_time_local blank for records that have been manually created (as date_time_utc will actually be local time)
        '''
        logging.debug('--')
        listOfRecords = self.ddbbObject.select("records","id_record,date,date_time_utc,date_time_local", "date_time_local is NULL")
        logging.debug("Found %d records in DB without date_time_local field populated" % (len(listOfRecords) ) )
        for record in listOfRecords:
            try:
                gpxfile = self.configuration.gpxdir+"/%s.gpx"%(record[0])
                dateFromUTC = Date().getDateTime(record[2])
                if os.path.isfile(gpxfile) : #GPX file exists for this record - probably not a manual record
                    date_time_local = str(dateFromUTC[1])
                    dateFromLocal = dateFromUTC[1].strftime("%Y-%m-%d")
                    if record[1] != dateFromLocal:
                        #date field incorrect - update it
                        logging.debug("Updating record id: %s with date: %s and date_time_local: %s" % (record[0], dateFromLocal, date_time_local) )
                        self.ddbbObject.update("records","date, date_time_local",[dateFromLocal, date_time_local], "id_record = %d" %record[0])
                    else:
                        #date field OK, just update date_time_local
                        logging.debug("Updating record id: %s with date_time_local: %s" % (record[0], date_time_local) )
                        self.ddbbObject.update("records","date_time_local",[date_time_local], "id_record = %d" %record[0])
                else: #Manual entry?
                    #For manual entries, the UTC time is the local time
                    #TODO figure out a way to correct this...
                    pass
            except Exception as e:
                print "Error updating record: " + str(record)
                print e
                logging.debug("Error updating record: " + str(record))
                logging.debug(str(e))
