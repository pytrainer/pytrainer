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

# Fixed some issues with MySql tables creation (email from Jonas Liljenfeldt)
class Sql:
    def __init__(self):
        self.db = None
    
    def connect(self, connection):
        self.db = connection

    def disconnect(self):
        self.db.close()
    
    def createDDBB(self):
        self.db.query("create database %s" %self.ddbb)
        
    def getTableList(self):
        tables = []
        result = self.freeExec('show tables')
        for row in result:
            tables.append(row[0])
        return tables
        
    def createTableDefault(self,tableName,columns):
        '''
        Creates a new table in database given name and column name and data types. New in version 1.7.0
        args:
            tableName - string with name of the table
            columns - dictionary containing column names and data types coming from definition
        returns: none'''
        #print self, tableName, columns
        logging.debug('>>')
        logging.info('Creating '+str(tableName)+' table with default values')
        logging.debug('Columns definition: '+str(columns))
        cur = self.db.cursor()
        sql = 'CREATE TABLE %s (' %(tableName)
        for entry in columns:
            if columns[entry].find('autoincrement') != -1:
                logging.debug("have a autoincrement field")
                fieldtype = columns[entry].replace('autoincrement', 'auto_increment')
                sql += '%s %s,' %(entry,fieldtype)
            else:
                sql += '%s %s,' %(entry,columns[entry])
        # Removing trailing comma
        sql = sql.rstrip(',')
        sql = sql+");"
        logging.debug('SQL sentence: '+str(sql))
        #print sql
        cur.execute(sql)
        logging.debug('<<')

    def insert(self,table, cells, values):
        val = values
        count = 0
        string = ""
        for i in val:
            if count>0:
                string+=","
            string+="""\"%s\"""" %i
            count = count+1
        sql = '''insert into %s (%s) values (%s)'''  %(table,cells,string)
        self.db.query(sql)
        self.db.commit()

    def freeExec(self,sql):
        #self.db.query(sql)
        cur = self.db.cursor()
        cur.execute(sql)
        retorno = []
        for row in cur.fetchall():
            retorno.append(row)
            self.db.commit()
        return retorno
    
    def delete(self,table,condition):
        sql = "delete from %s where %s"  %(table,condition)
        self.db.query(sql)
        self.db.commit()

    def select(self,table,cells,condition, mod=None):
        if condition != None:
            self.db.query("""select %s from %s where %s""" %(cells,table,condition))
        else:
            self.db.query("""select %s from %s """ %(cells,table))
        r = self.db.store_result()
        retorno = []
        while 1==1:
            sublist = r.fetch_row()
            if len(sublist)>0:
                retorno.append(sublist[0])
            else:
                break
        return retorno

    def update (self,table,cells,values,condition):
        cells = cells.split(",")
        count = 0
        string = ""
        for val in values:
            if count>0:
                string+=","
            string += """%s="%s" """ %(cells[count],values[count])
            count = count+1

        string +=" where %s" %condition
        sql = "update %s set %s" %(table,string)
        self.db.query(sql)
        self.db.commit()
        
    def retrieveTableInfo(self,tableName):
        cur = self.db.cursor()
        sql = "desc %s;" %tableName
        cur.execute(sql)
        tableInfo = []
        for row in cur:
            tableInfo.append(row)
        return tableInfo
        return
    
    def addColumn(self,tableName,columnName,dataType):
        if dataType.find('autoincrement') != -1:
            dataType = dataType.replace('autoincrement', 'auto_increment')
        sql = "alter table %s add %s %s" %(tableName,columnName,dataType)
        logging.debug("Trying SQL: %s" % sql)
        try:
            self.freeExec(sql)
        except:
            logging.error('Not able to add/change column '+columnName+' to table '+tableName)
            traceback.print_exc()
            
    def createDatabaseBackup(self):
        logging.info("Unable to create backup for MySQL DB")
