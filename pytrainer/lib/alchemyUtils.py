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
import traceback
import datetime
from sqlalchemy import create_engine

class Sql:
    def __init__(self, configuration):
        self.dbtype = configuration.getValue("pytraining", "prf_ddbb")
        self.dbname = configuration.getValue("pytraining", "prf_ddbbname")
        if self.dbtype == 'sqlite':
            self.dburl = "sqlite:///%s/pytrainer.ddbb" % configuration.confdir
        else:
            self.dburl = "{dbtype}://{user}:{passwd}@{host}/{db}".format(dbtype=self.dbtype, db=self.dbname,
                                                                         user=configuration.getValue("pytraining", "prf_ddbbuser"),
                                                                         passwd=configuration.getValue("pytraining", "prf_ddbbpass"),
                                                                         host=configuration.getValue("pytraining", "prf_ddbbhost"))
        logging.debug("Dburl is %s", self.dburl)
        self.engine = create_engine(self.dburl, logging_name='db')

    def get_connection_url(self):
        return self.dburl

    def connect(self):
        self.engine.connect()
        return (True, "OK")

    def disconnect(self):
        self.engine.dispose()

    def createDDBB(self):
        if not self.dbtype == 'sqlite':
            self.engine.execute("create database %s" % self.dbname)

    def createTableDefault(self, tableName, columns):
        '''22.11.2009 - dgranda
        Creates a new table in database given name and column name and data types. New in version 1.7.0
        args:
            tableName - string with name of the table
            columns - dictionary containing column names and data types coming from definition
        returns: none'''
        logging.debug('>>')
        logging.info('Creating %s table with default values', tableName)
        logging.debug('Columns definition: %s', columns)
        sql = 'CREATE TABLE %s (' %(tableName)
        for entry in columns:
            if self.dbtype == 'mysql' and columns[entry].find('autoincrement') != -1:
                logging.debug("have a autoincrement field")
                fieldtype = columns[entry].replace('autoincrement', 'auto_increment')
                sql += '%s %s,' %(entry, fieldtype)
            else:
                sql += '%s %s,' %(entry, columns[entry])
        # Removing trailing comma
        sql = sql.rstrip(',')
        sql = sql+");"
        logging.debug('SQL sentence: %s', sql)
        self.engine.execute(sql)
        logging.debug('<<')

    def insert(self, table, cells, values):
        logging.debug('>>')
        val = values
        count = 0
        string = ""
        for i in val:
            if count > 0:
                string += ","
            string += self._to_sql_value(i)
            count = count+1
        sql = "insert into %s (%s) values (%s)" % (table, cells, string)
        logging.debug('SQL sentence: %s', sql)
        self.engine.execute(sql)
        logging.debug('<<')

    def _to_sql_value(self, value):
        logging.debug('>>')
        logging.debug('Value: %s | type: %s ', value, type(value))
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

    def freeExec(self, sql):
        retorno = []
        for row in self.engine.execute(sql):
            retorno.append(row)
        return retorno

    def delete(self, table, condition):
        sql = "delete from %s where %s" % (table, condition)
        self.engine.execute(sql)

    def update(self, table, cells, values, condition):
        cells = cells.split(",")
        count = 0
        string = ""
        for val in values:
            if count > 0:
                string += ","
            string += """%s=%s """ %(cells[count], self._to_sql_value(values[count]))
            count = count+1

        string += " where %s" % condition
        sql = "update %s set %s" %(table, string)
        self.engine.execute(sql)

    def select(self, table, cells, condition, mod=None):
        sql = "select %s from %s" % (cells, table)
        if condition is not None:
            sql = "%s where %s" % (sql, condition)
        if mod is not None:
            sql = "%s %s" % (sql, mod)
        retorno = []
        for row in self.engine.execute(sql):
            retorno.append(row)
        return retorno

    def addColumn(self, tableName, columnName, dataType):
        if self.dbtype == 'mysql' and dataType.find('autoincrement') != -1:
            dataType = dataType.replace('autoincrement', 'auto_increment')
        sql = "alter table %s add %s %s" %(tableName, columnName, dataType)
        logging.debug("Trying SQL: %s", sql)
        try:
            self.freeExec(sql)
        except:
            logging.error('Not able to add/change column %s to table %s', columnName, tableName)
            traceback.print_exc()


    def createDatabaseBackup(self):
        logging.info("Unable to create backup for Alchemy DB")
