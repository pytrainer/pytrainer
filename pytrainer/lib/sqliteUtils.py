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
import sys
try:
	from sqlite3 import dbapi2 as sqlite
except ImportError:
	logging.error('Not able to find sqlite2 module (new in python 2.5)')
	from pysqlite2 import dbapi2 as sqlite
	logging.info('Using pysqlite2 module to access DB. Think about upgrading to python 2.5!')
from system import checkConf
from logs import Log

class Sql:
	def __init__(self,host=None, ddbb = None, user = None, password = None):
		self.db = None
		conf = checkConf()
		confdir = conf.getValue("confdir")
		self.ddbb = "%s/pytrainer.ddbb" %confdir
		self.log = Log()
	
	def connect(self):
		#si devolvemos 1 ha ido todo con exito
		self.db = sqlite.connect(self.ddbb)
		#probamos si estan las tablas creadas, y sino.. las creamos
		try: 
			self.select("records","id_record","1=1 limit 0,1")
		except:
			self.createTables()
		return 1

	def disconnect(self):
		self.db.close()
	
	def createDDBB(self):
		pass

	def createTables(self):
		cur = self.db.cursor()	
		#creamos la tabla sports
		sql = """CREATE TABLE sports (
			id_sports integer primary key autoincrement, 
			name varchar (100),
			weight float,
			met float
			);"""
		cur.execute(sql)

		#creamos la tabla records
		sql = """CREATE TABLE records (
			id_record integer primary key autoincrement ,
			date date,
			sport integer,
			distance float,
			time varchar (200),
			beats float,
			average float,
			calories int,
			comments text,
			gpslog varchar(200),
			title varchar(200),
			upositive float,
			unegative float,
			maxspeed float,
			maxpace float,
			pace float,
			maxbeats float,
         date_time_utc varchar2(20)
			) ;"""
		cur.execute(sql)

		#creamos la tabla waypoints
		sql = """CREATE TABLE waypoints (
			id_waypoint integer primary key autoincrement ,
			lat float,
			lon float,
			ele float,
			comment varchar (240),
			time date,
			name varchar (200),
			sym varchar (200)
			) ;"""
		cur.execute(sql)

		self.insert("sports","name",["Mountain Bike"]);
		self.insert("sports","name",["Bike"]);
		self.insert("sports","name",["Run"]);

	def createTableDefault(self,tableName,columns):
		"""22.11.2009 - dgranda
		Creates a new table in database given name and column name and data types. New in version 1.7.0
		args:
			tableName - string with name of the table
			columns - dictionary containing column names and data types coming from definition
		returns: none"""
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
		
	def addWaipoints2ddbb(self):
		cur = self.db.cursor()	
		sql = """CREATE TABLE waypoints (
			id_waypoint integer primary key autoincrement ,
			lat float,
			lon float,
			ele float,
			comment varchar (240),
			time date,
			name varchar (200),
			sym varchar (200)
			) ;"""
		cur.execute(sql)
		
	def insert(self,table, cells, values):
		cur = self.db.cursor()	
		val = values
		count = 0
		string = ""
		for i in val:
			if count>0:
				string+=","
			string+="""\"%s\"""" %i
			count = count+1
		sql = "insert into %s (%s) values (%s)"  %(table,cells,string)
		self.log.run(sql)
		cur.execute(sql)
		self.db.commit()

	def freeExec(self,sql):
		cur = self.db.cursor()
		self.log.run(sql)
		cur.execute(sql)
		retorno = []
		for row in cur:
			retorno.append(row)
		self.db.commit()
		return retorno

	def delete(self,table,condition):
		cur = self.db.cursor()	
		sql = "delete from %s where %s"  %(table,condition)
		self.log.run(sql)
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
			string += """%s="%s" """ %(cells[count],values[count])
			count = count+1

		string +=" where %s" %condition
		sql = "update %s set %s" %(table,string)
		self.log.run(sql)
		cur.execute(sql)
		self.db.commit()

	def select(self,table,cells,condition):
		cur = self.db.cursor()	
		if condition != None:
			sql = "select %s from %s where %s" %(cells,table,condition)
		else:
			sql = "select %s from %s " %(cells,table)
		self.log.run(sql)
		cur.execute(sql)
		retorno = []
		for row in cur:
			retorno.append(row)
		return retorno

	def checkTable(self,tableName,columns):
		"""19.11.2009 - dgranda
		Checks column names and values from table and adds something if missed. New in version 1.7.0
		args:
			tableName - string with name of the table
			columns - dictionary containing column names and data types coming from definition
		returns: none"""
		logging.debug('>>')
		logging.info('Inspecting '+str(tableName)+' table')
		logging.debug('Columns definition: '+str(columns))

		# Retrieving data from DB
		tableInfo = self.retrieveTableInfo(tableName)
		#logging.debug('Raw data retrieved from DB '+str(tableName)+': '+str(tableInfo))

		# Comparing data retrieved from DB with what comes from definition
		columnsDB = {}
		for field in tableInfo:
			newField = {field[1]:field[2]}
			columnsDB.update(newField)
		logging.debug('Useful data retrieved from '+str(tableName)+' in DB: '+str(columnsDB))

		# http://mail.python.org/pipermail/python-list/2002-May/142854.html - not correct URL....
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
		sql = "PRAGMA table_info(%s);" %tableName
		cur.execute(sql)
		tableInfo = []
		for row in cur:
			tableInfo.append(row)
		return tableInfo

	def addColumn(self,tableName,columnName,dataType):
		sql = "alter table %s add %s %s" %(tableName,columnName,dataType)
		try:
			self.freeExec(sql)
		except:
			logging.error('Not able to add/change column '+columnName+' to table '+tableName)
			#traceback.print_exc()

