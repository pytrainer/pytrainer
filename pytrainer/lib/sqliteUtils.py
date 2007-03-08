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

from pysqlite2 import dbapi2 as sqlite
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
	
	def createDDBB(self):
		pass

	def createTables(self):
		cur = self.db.cursor()	
		#creamos la tabla sports
		sql = """CREATE TABLE sports (
			id_sports integer primary key autoincrement, 
			name varchar (100)
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
			unegative float
			) ;"""
		cur.execute(sql)

		self.insert("sports","name",["Mountain Bike"]);
		self.insert("sports","name",["Bike"]);
		self.insert("sports","name",["Run"]);
		
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
			string += """%s='%s'""" %(cells[count],values[count])
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

