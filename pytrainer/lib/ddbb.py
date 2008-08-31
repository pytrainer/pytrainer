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

class DDBB:
	def __init__(self, configuration):
		ddbb_type = configuration.getValue("pytraining","prf_ddbb")
		if ddbb_type == "mysql":
			from mysqlUtils import Sql
		if ddbb_type == "sqlite":
			from sqliteUtils import Sql
		
		ddbb_host = configuration.getValue("pytraining","prf_ddbbhost")
		ddbb = configuration.getValue("pytraining","prf_ddbbname")
		ddbb_user = configuration.getValue("pytraining","prf_ddbbuser")
		ddbb_pass = configuration.getValue("pytraining","prf_ddbbpass")
		self.ddbbObject = Sql(ddbb_host,ddbb,ddbb_user,ddbb_pass)
		
	def connect(self):
		#si devolvemos 1 ha ido todo con exito
		#con 0 es que no estaba la bbdd creada
		#con 1 imposible conectar a la maquina.
		var = self.ddbbObject.connect()
		if var == 0:
			self.ddbbObject.createDDBB()
			self.ddbbObject.connect()
			self.ddbbObject.createTables()
			var = 1
		return var

	def disconnect(self):
		self.ddbbObject.disconnect()

	def build_ddbb(self):
		self.ddbbObject.createDDBB()
		self.ddbbObject.connect()
		self.ddbbObject.createTables()
		self.ddbbObject.createTableVersion()

	def select(self,table,cells,condition=None):
		return self.ddbbObject.select(table,cells,condition)

	def insert(self,table,cells,values):
		self.ddbbObject.insert(table,cells,values)
	
	def delete(self,table,condition):
		self.ddbbObject.delete(table,condition)

	def update(self,table,cells,value,condition):
		self.ddbbObject.update(table,cells,value,condition)
	
	def lastRecord(self,table):
		if table=="records":
			id = "id_record"
		if table=="sports":
			id = "id_sport"
		if table=="waypoints":
			id = "id_waypoint" 
		sql = "select %s from %s order by %s Desc limit 0,1" %(id,table,id)
		ret_val = self.ddbbObject.freeExec(sql)
		return ret_val[0][0]


	def addTitle2ddbb(self):
		#this function add a title column in
		#the record ddbb. New in 0.9.9 version
		sql = "alter table records add title varchar(200)"
		try:
			self.ddbbObject.freeExec(sql)
		except:
			logging.error('Column title already exists in DB. Printing traceback and continuing')
			traceback.print_exc()
		
	def addUnevenness2ddbb(self):
		#this function add accumulated unevennes columns in
		#the record ddbb. New in 1.3.2 version
		sql = "alter table records add upositive float"
		try:
			self.ddbbObject.freeExec(sql)
		except:
			logging.error('Column upositive already exists in DB. Printing traceback and continuing')
			traceback.print_exc()
		sql = "alter table records add unegative float"
		try:
			self.ddbbObject.freeExec(sql)
		except:
			logging.error('Column unegative already exists in DB. Printing traceback and continuing')
			traceback.print_exc()
			
	def addWaypoints2ddbb(self):
		#adds waipoints table to database
		try:
			self.ddbbObject.addWaipoints2ddbb()
		except:
			logging.error('Waypoints table already exists in DB. Printing traceback and continuing')
			traceback.print_exc()
	
	def updatemonth(self):
		#this is a function to repair a bug from
		#pytrainer 0.9.5 and previus
		listOfRecords = self.ddbbObject.select("records","id_record,date", None)
		for record in listOfRecords:
			rec = record[1].split("-")
			newmonth = int(rec[1])+1
			newdate = "%s-%d-%s" %(rec[0],newmonth,rec[2])
			self.ddbbObject.update("records","date",[newdate], "id_record = %d" %record[0])

	def updateDateFormat(self):
		#this is a function to repair a bug from 
		#pytrainer 0.9.8 and previus
		listOfRecords = self.ddbbObject.select("records","id_record,date", None)
		for record in listOfRecords:
			try:
				rec = record[1].split("-")
				newdate = "%0.4d-%0.2d-%0.2d" %(int(rec[0]),int(rec[1]),int(rec[2]))
				self.ddbbObject.update("records","date",[newdate], "id_record = %d" %record[0])
			except:
				print record
			
	def addweightandmet2ddbb(self):
		#this function add weight extra and met fields to sports table
		sql = "alter table sports add weight float"
		try:
			self.ddbbObject.freeExec(sql)
		except:
			logging.error('Column weight already exists in DB. Printing traceback and continuing')
			traceback.print_exc()
		sql = "alter table sports add met float"
		try:
			self.ddbbObject.freeExec(sql)
		except:
			logging.error('Column met already exists in DB. Printing traceback and continuing')
			traceback.print_exc()
			
	def checkmettable(self):
		sql = "alter table sports add met float"
		try:
			self.ddbbObject.freeExec(sql)
		except:
			logging.error('Column met already exists in DB. Printing traceback and continuing')
			traceback.print_exc()

	def addpaceandmax2ddbb(self):
		sql = "alter table records add maxspeed float"
		try:
			self.ddbbObject.freeExec(sql)
		except:
			logging.error('Column maxspeed already exists in DB. Printing traceback and continuing')
			traceback.print_exc()
		sql = "alter table records add maxpace float"
		try:
			self.ddbbObject.freeExec(sql)
		except:
			logging.error('Column maxpace already exists in DB. Printing traceback and continuing')
			traceback.print_exc()
		sql = "alter table records add pace float"
		try:
			self.ddbbObject.freeExec(sql)
		except:
			logging.error('Column pace already exists in DB. Printing traceback and continuing')
			traceback.print_exc()
		sql = "alter table records add maxbeats float"
		try:
			self.ddbbObject.freeExec(sql)
		except:
			logging.error('Column maxbeats already exists in DB. Printing traceback and continuing')
			traceback.print_exc()
		
	def addDateTimeUTC2ddbb(self):
		sql = "alter table records add date_time_utc varchar2(20)"
		try:
			self.ddbbObject.freeExec(sql)
		except:
			logging.error('Column date_time_utc already exists in DB. Printing traceback and continuing')
			traceback.print_exc()
		
	def shortFromLocal(self, getSport=True): # Check LEFT and RIGHT JOINS with people with multiple sports
		if getSport is True:
			sql = "select sports.name,records.date_time_utc from sports INNER JOIN records ON sports.id_sports = records.sport"
		else:
			sql = "select records.date_time_utc from sports INNER JOIN records ON sports.id_sports = records.sport"
		return self.ddbbObject.freeExec(sql)

