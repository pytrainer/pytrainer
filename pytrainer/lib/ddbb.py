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
from pytrainer.lib.date import Date

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
        #si devolvemos 1 ha ido todo con exito      : return 1 if all successful
        #con 0 es que no estaba la bbdd creada      : 0 is DB not created
        #con -1 imposible conectar a la maquina.    : -1 is impossible to connect to the host
        var = self.ddbbObject.connect()
        if var == 0:
            self.ddbbObject.createDDBB()
            self.ddbbObject.connect()
            self.ddbbObject.createTables()
            var = 1
        return var

    def disconnect(self):
        self.ddbbObject.disconnect()

    def build_ddbb(self): #TODO Is this needed?
        self.ddbbObject.createDDBB()
        self.ddbbObject.connect()
        self.ddbbObject.createTables()
        self.ddbbObject.createTableVersion()

    def select(self,table,cells,condition=None):
        return self.ddbbObject.select(table,cells,condition)

    def select_dict(self,table,cells,condition=None):
        '''
        Function to query DB
        -- inputs
        ---- table - string tablename(s)
        ---- cells - list of cells to select
        ---- condition - string to fit SQL where clause or None
        -- returns
        ---- list of dicts with cells as keys
        '''
        return_value = []
        #Only query db if table and cells are supplied
        if table is not None and cells is not None:
            cellString = ','.join(cells) #create cell list string
            results = self.ddbbObject.select(table,cellString,condition)
            for result in results:
                dict = {}
                #Loop through cells and create dict of results
                for i, cell in enumerate(cells):
                    dict[cell] = result[i]
                return_value.append(dict)
        return return_value

    def insert(self,table,cells,values):
        self.ddbbObject.insert(table,cells,values)

    def delete(self,table,condition):
        self.ddbbObject.delete(table,condition)

    def update(self,table,cells,value,condition):
        self.ddbbObject.update(table,cells,value,condition)

    def lastRecord(self,table):
        id = "id_" + table[:-1] #prune 's' of table name and pre-pend 'id_' to get id column
        sql = "select %s from %s order by %s Desc limit 0,1" %(id,table,id)
        ret_val = self.ddbbObject.freeExec(sql)
        return ret_val[0][0]

    def checkDBIntegrity(self):
        """17.11.2009 - dgranda
        Retrieves tables and columns from database, checks current ones and adds something if missed. New in version 1.7.0
        args: none
        returns: none"""
        logging.debug('>>')
        logging.info('Checking PyTrainer database')
        if self.ddbb_type != "sqlite":
            logging.error('Support for MySQL database is decommissioned, please migrate to SQLite. Exiting check')
            exit(-2)
        #Define the tables and their columns that should be in the database
        tablesList = {  "records":{     "id_record":"integer primary key autoincrement",
                                        "date":"date",
                                        "sport":"integer",
                                        "distance":"float",
                                        "time":"varchar(200)",
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
                                        "date_time_local":"varchar2(20)",
                                        "date_time_utc":"varchar2(20)",
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
                        }
        try:
            tablesDBT = self.ddbbObject.select("sqlite_master","name", "type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY name")
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
            self.createDatabaseBackup()
        except:
            logging.error('Not able to make a copy of current DB. Printing traceback and exiting')
            traceback.print_exc()
            exit(-1)

        #Check Tables
        for entry in tablesList:
            if entry not in tablesDB:
                logging.warn('Table '+str(entry)+' does not exist in DB')
                self.ddbbObject.createTableDefault(entry,tablesList[entry])
            else:
                self.ddbbObject.checkTable(entry,tablesList[entry])

        #Run any functions to update or correct data
        #These functions _must_ be safe to run at any time (i.e. not be version specfic or only safe to run once)
        self.populate_date_time_local()
        logging.debug('<<')

    def createDatabaseBackup(self):
        logging.debug('>>')
        logging.debug('Database path: '+str(self.ddbb_path))
        result = commands.getstatusoutput('gzip -c '+self.ddbb_path+' > '+self.ddbb_path+'_`date +%Y%m%d_%H%M`.gz')
        if result[0] != 0:
            raise Exception, "Copying current database does not work, error #"+str(result[0])
        else:
            logging.info('Database backup successfully created')
        logging.debug('<<')

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
