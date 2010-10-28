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

import _mysql_exceptions
import MySQLdb
import logging

# Fixed some issues with MySql tables creation (email from Jonas Liljenfeldt)
class Sql:
    def __init__(self,host=None, ddbb = None, user = None, password = None, configuration = None):
        self.ddbb_user = user
        self.ddbb_pass = password
        self.ddbb_host = host
        self.ddbb = ddbb
        self.db = None
    
    def connect(self):
        #si devolvemos 1 ha ido todo con exito
        #con 0 es que no estaba la bbdd creada
        #con -1 imposible conectar a la maquina.
        try:
            self.db=MySQLdb.connect(
                host=self.ddbb_host,
                user=self.ddbb_user,
                passwd=self.ddbb_pass,
                db=self.ddbb)
            return (True, "OK")
        except _mysql_exceptions.OperationalError as e:
            error_no, error_description = e
            print "ERROR: An error occured while connecting to MySQL DB (%s) %s" % (error_no, error_description)
            if error_no == 1049:
                #Unknown DB - try to create?
                print "Unknown DB given, attempting to create a new DB"
                try:
                    #Connect to DB without specifying the DB
                    self.db=MySQLdb.connect(host=self.ddbb_host, user=self.ddbb_user, passwd=self.ddbb_pass)
                    #Create DB
                    self.createDDBB()
                    #Reconnect to new DB
                    self.db=MySQLdb.connect(host=self.ddbb_host, user=self.ddbb_user, passwd=self.ddbb_pass, db=self.ddbb)
                    return (True, "OK")
                except Exception as e:
                    #No good - so stop
                    print type(e)
                    print e
                    logging.error("Unable to connect to MySQL DB")
                    return (False, "Unable to connect to MySQL DB")
        except Exception as e:
            logging.error("Unable to connect to MySQL DB")
            print "ERROR: Unable to connect to MySQL DB"
            print type(e)
            print e
            return (False, "Unable to connect to MySQL DB")
    
    def disconnect(self):
        self.db.close()
    
    def createDDBB(self):
        self.db.query("create database %s" %self.ddbb)
        
    def getTableList(self):
        return self.freeExec('show tables')
        
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
        
    def checkTable(self,tableName,columns):
        '''
        Checks column names and values from table and adds something if missed. New in version 1.7.0
        args:
            tableName - string with name of the table
            columns - dictionary containing column names and data types coming from definition
        returns: none'''
        logging.debug('>>')
        logging.info('Inspecting '+str(tableName)+' table')
        logging.debug('Columns definition: '+str(columns))

        # Retrieving data from DB
        tableInfo = self.retrieveTableInfo(tableName)
        logging.debug('Raw data retrieved from DB '+str(tableName)+': '+str(tableInfo))
        #print('Raw data retrieved from DB '+str(tableName)+': '+str(tableInfo))
        #Raw data retrieved from DB sports: [('met', 'float', 'YES', '', None, ''), ('id_sports', 'int(11)', 'NO', 'PRI', None, 'auto_increment'), ('max_pace', 'int(11)', 'YES', '', None, ''), ('name', 'varchar(100)', 'YES', '', None, ''), ('weight', 'float', 'YES', '', None, '')]

        # Comparing data retrieved from DB with what comes from definition
        columnsDB = {}
        for field in tableInfo:
            newField = {field[0]:field[1]}
            columnsDB.update(newField)
        logging.debug('Useful data retrieved from '+str(tableName)+' in DB: '+str(columnsDB))
        #print('Useful data retrieved from '+str(tableName)+' in DB: '+str(columnsDB))

        # http://mail.python.org/pipermail/python-list/2002-May/141458.html
        #tempDict = dict(zip(columns,columns))
        tempDict = dict(columns)
        #Test for columns that are in DB that shouldn't be
        result = [x for x in columnsDB if x not in tempDict]
        #Test for columns that are not in the DB that should be
        result2 = [x for x in tempDict if x not in columnsDB]

        logging.debug("Columns in DB that shouldnt be: "+str(result))
        logging.debug("Columns missing from DB: "+str(result2))
        
        table_ok = True
        if len(result) > 0:
            logging.debug('Found columns in DB that should not be: '+ str(result))
            table_ok = False
            for entry in result:
                logging.debug('Column '+ str(entry) +' in DB but not in definition')
                print "Column %s in DB but not in definition - please fix manually" % (str(entry))
                print "#TODO need to add auto fix code"
                sys.exit(1)
        if len(result2) > 0: # may have also different data type
            logging.debug('Found columns missed in DB: '+ str(result2))
            table_ok = False
            for entry in result2:
                logging.debug('Column '+ str(entry) +' not found in DB')
                self.addColumn(tableName,str(entry),columns[entry])
        if table_ok:
            logging.info('Table '+ str(tableName) +' is OK')
        logging.debug('<<')
        
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
        logging.debug('>>')
        logging.info("Unable to create backup for MySQL DB")
        logging.debug('<<')
