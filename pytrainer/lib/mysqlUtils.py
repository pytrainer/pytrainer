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

import _mysql

class Sql:
	def __init__(self,host=None, ddbb = None, user = None, password = None):
		self.ddbb_user = user
		self.ddbb_pass = password
		self.ddbb_host = host
		self.ddbb = ddbb
		self.db = None
	
	def connect(self):
		#si devolvemos 1 ha ido todo con exito
		#con 0 es que no estaba la bbdd creada
		#con 1 imposible conectar a la maquina.
		try:
			self.db=_mysql.connect(
				host=self.ddbb_host,
				user=self.ddbb_user,
				passwd=self.ddbb_pass,
				db=self.ddbb)
			return 1
		except:
			try:
				self.db=_mysql.connect(
					host=self.ddbb_host,
					user=self.ddbb_user,
					passwd=self.ddbb_pass)
				return 0
			except:
				return -1
	
	def disconnect(self):
		self.db.close()
	
	def createDDBB(self):
		self.db.query("create database %s" %self.ddbb)

	def createTables(self):
		#creamos la tabla sports
		self.db.query("""CREATE TABLE `sports` (
			`id_sports` INT( 11 ) NOT NULL AUTO_INCREMENT ,
			`name` VARCHAR( 100 ) NOT NULL ,
			`weight` FLOAT NOT NULL ,
			`met` FLOAT NOT NULL ,
			INDEX ( `id_sports` )
			) ENGINE = MYISAM ;""")

		#creamos la tabla records
		self.db.query("""CREATE TABLE `records` (
			`id_record` INT( 11 ) NOT NULL AUTO_INCREMENT ,
			`date` DATE NOT NULL ,
			`sport` INT( 11 ) NOT NULL ,
			`distance` FLOAT NOT NULL ,
			`time` VARCHAR( 200 ) NOT NULL ,
			`beats` FLOAT NOT NULL ,
			`average` FLOAT NOT NULL ,
			`calories` INT( 11 ) NOT NULL ,
			`comments` TEXT NOT NULL ,
			`gpslog` VARCHAR( 200 ) NOT NULL ,
			`title` VARCHAR( 200 ) NOT NULL ,
			`upositive` FLOAT NOT NULL ,
			`unegative` FLOAT NOT NULL ,
			`maxspeed` FLOAT, NOT NULL,
			maxpace FLOAT NOT NULL,
			pace FLOAT NOT NULL,
			maxbeats FLOAT NOT NULL,
			INDEX ( `id_record` )
			) ENGINE = MYISAM ;""")
		
		#creamos la tabla waypoints
		sql = """CREATE TABLE waypoints (
			id_waypoint INT(11) NOT NULL AUTO_INCREMENT ,
			lat float NOT NULL,
			lon float NOT NULL,
			ele float NOT NULL,
			time date NOT NULL,
			name varchar (200) NOT NULL,
			sym varchar (200) NOT NULL,
			comment varchar (240) NOT NULL,
			INDEX (id_waypoint)
			) ENGINE = MYISAM ;"""
		self.db.query(sql)
	
		self.insert("sports","name",["Mountain Bike"])
		self.insert("sports","name",["Bike"])
		self.insert("sports","name",["Run"])
	def addWaipoints2ddbb(self):
		sql = """CREATE TABLE waypoints (
			id_waypoint INT(11) NOT NULL AUTO_INCREMENT ,
			lat float NOT NULL,
			lon float NOT NULL,
			ele float NOT NULL,
			time date NOT NULL,
			name varchar (200) NOT NULL,
			sym varchar (200) NOT NULL,
			comment varchar (240) NOT NULL,
			INDEX (id_waypoint)
			) ENGINE = MYISAM ;"""
		self.db.query(sql)

	def insert(self,table, cells, values):
		val = values
		count = 0
		string = ""
		for i in val:
			if count>0:
				string+=","
			string+="""\"%s\"""" %i
			count = count+1
		self.db.query("""insert into %s (%s) values (%s)"""  %(table,cells,string))

	def freeExec(self,sql):
		self.db.query(sql)
	
	def delete(self,table,condition):
		sql = "delete from %s where %s"  %(table,condition)
		self.db.query(sql)

	def select(self,table,cells,condition):
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
