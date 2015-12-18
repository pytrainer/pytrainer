# -*- coding: iso-8859-1 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net
# vud1@grupoikusnet.com
# Jakinbidea & Grupo Ikusnet Developer

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
import sys, traceback, commands
import datetime
try:
    from sqlite3 import dbapi2 as sqlite
except ImportError:
    logging.error('Not able to find sqlite2 module (new in python 2.5)')
    from pysqlite2 import dbapi2 as sqlite
    logging.info('Using pysqlite2 module to access DB. Think about upgrading to python 2.5!')
    
class Sql:
    def __init__(self,host=None, ddbb = None, user = None, password = None, configuration = None):
        self.db = None
        confdir = configuration.confdir
        self.ddbb = "%s/pytrainer.ddbb" %confdir
        self.url = "sqlite:///" + self.ddbb
        
    def get_connection_url(self):
        return self.url
    
    def connect(self):
        #si devolvemos 1 ha ido todo con exito
        self.db = sqlite.connect(self.ddbb)
        return (True, "OK")
        #probamos si estan las tablas creadas, y sino.. las creamos
        '''try: 
            self.select("records","id_record","1=1 limit 0,1")
        except:
            self.createTables()
        return 1'''

    def disconnect(self):
        self.db.close()
    
    def createDDBB(self):
        pass
        
    def getTableList(self):
        tmpList = self.select("sqlite_master","name", "type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY name")
        # The instruction above returns a list of tuples, going for a simple list
        newList = []
        for entry in tmpList:
            newList.append(entry[0])
        return newList

    def createTableDefault(self,tableName,columns):
        '''22.11.2009 - dgranda
        Creates a new table in database given name and column name and data types. New in version 1.7.0
        args:
            tableName - string with name of the table
            columns - dictionary containing column names and data types coming from definition
        returns: none'''
        logging.debug('>>')
        logging.info('Creating '+str(tableName)+' table with default values')
        logging.debug('Columns definition: '+str(columns))
        cur = self.db.cursor()
        sql = 'CREATE TABLE %s (' %(tableName)
        for entry in columns:
            sql += '%s %s,' %(entry,columns[entry])
        # Removing trailing comma
        sql = sql.rstrip(',')
        sql = sql+");"
        logging.debug('SQL sentence: '+str(sql))
        cur.execute(sql)
        logging.debug('<<')
              
    def insert(self,table, cells, values):
        logging.debug('>>')
        cur = self.db.cursor()  
        val = values
        count = 0
        string = ""
        for i in val:
            if count>0:
                string+=","
            string+= self._to_sql_value(i)
            count = count+1
        sql = "insert into %s (%s) values (%s)"  %(table,cells,string)
        logging.debug('SQL sentence: '+str(sql))
        cur.execute(sql)
        self.db.commit()
        logging.debug('<<')
        
    def _to_sql_value(self, value):
        logging.debug('>>')
        logging.debug('Value: %s | type: %s ' %(value,type(value)))
        if value == None:
            return "null"
        elif type(value) in [str, unicode]:
            return "\"" + value + "\""
        elif type(value) == datetime.datetime:
            return value.strftime("\"%Y-%m-%d %H:%M:%S%z\"")
        elif type(value) == datetime.date:
            return value.strftime("\"%Y-%m-%d\"")
        else:
            return str(value)
        logging.debug('<<')

    def freeExec(self,sql):
        cur = self.db.cursor()
        cur.execute(sql)
        retorno = []
        for row in cur:
            retorno.append(row)
        self.db.commit()
        return retorno

    def delete(self,table,condition):
        cur = self.db.cursor()  
        sql = "delete from %s where %s"  %(table,condition)
        cur.execute(sql)
        self.db.commit()

    def update(self,table,cells,values, condition):
        cur = self.db.cursor()  
        cells = cells.split(",")
        count = 0
        string = ""
        for val in values:
            if count>0:
                string+=","
            string += """%s=%s """ %(cells[count], self._to_sql_value(values[count]))
            count = count+1

        string +=" where %s" %condition
        sql = "update %s set %s" %(table,string)
        cur.execute(sql)
        self.db.commit()

    def select(self,table,cells,condition, mod=None):
        cur = self.db.cursor()
        sql = "select %s from %s" %(cells,table)
        if condition is not None:
            sql = "%s where %s" % (sql, condition)
        if mod is not None:
            sql = "%s %s" % (sql, mod)
        '''if condition != None:
            sql = "select %s from %s where %s" %(cells,table,condition)
        else:
            sql = "select %s from %s " %(cells,table)'''
        cur.execute(sql)
        retorno = []
        for row in cur:
            retorno.append(row)
        return retorno

    def retrieveTableInfo(self,tableName):
        cur = self.db.cursor()
        sql = "PRAGMA table_info(%s);" %tableName
        cur.execute(sql)
        tableInfo = []
        for row in cur:
            tableInfo.append(row)
        return tableInfo

    def addColumn(self,tableName,columnName,dataType):
        sql = "alter table %s add %s %s" %(tableName,columnName,dataType)
        logging.debug("Trying SQL: %s" % sql)
        try:
            self.freeExec(sql)
        except:
            logging.error('Not able to add/change column '+columnName+' to table '+tableName)
            traceback.print_exc()


    def createDatabaseBackup(self):
        logging.info("Creating compressed copy of current DB")
        logging.debug('Database path: '+str(self.ddbb))
        result = commands.getstatusoutput('gzip -c '+self.ddbb+' > '+self.ddbb+'_`date +%Y%m%d_%H%M`.gz')
        if result[0] != 0:
            raise Exception, "Copying current database does not work, error #"+str(result[0])
        logging.info('Database backup successfully created')
