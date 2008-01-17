# -*- coding: iso-8859-1 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net

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

import os
import shutil

from gui.windowrecord import WindowRecord
from gui.dialogselecttrack import DialogSelectTrack
from lib.ddbb import DDBB
from lib.xmlUtils import XMLParser
from lib.system import checkConf
from lib.date import Date
from lib.gpx import Gpx

class Record:
	def __init__(self, data_path = None, parent = None, version=None):
		self.parent = parent
		self.data_path = data_path
		self.date = Date()
		self.conf = checkConf()
		self.filename = self.conf.getValue("conffile")
		self.configuration = XMLParser(self.filename)
		self.ddbb = DDBB(self.configuration)
		self.ddbb.connect()
		#hack for pytrainer 0.9.5 and previous
		if self.configuration.getOption("version")=="1.0":
			self.ddbb.updatemonth()
		if self.configuration.getOption("version")<="0.9.8":
			self.ddbb.updateDateFormat()
		if self.configuration.getOption("version")<="0.9.8.2":
			self.ddbb.addTitle2ddbb()
		if self.configuration.getOption("version")<="1.3.1":
			self.ddbb.addUnevenness2ddbb()
		if self.configuration.getOption("version")<="1.4.1.1":
			self.ddbb.addWaypoints2ddbb()
		if self.configuration.getOption("version")<="1.4.2":
			try:
				self.ddbb.addWaypoints2ddbb()
			except:
				pass
		if self.configuration.getOption("version")<="1.5.0":
			self.ddbb.addweightandmet2ddbb()
		if self.configuration.getOption("version")<version:
			self.configuration.setVersion(version)

        def newRecord(self, list_sport, date, title=None, distance=None, time=None, upositive=None, unegative=None, bpm=None, calories=None, comment=None):
		self.recordwindow = WindowRecord(self.data_path, list_sport,self, date, title, distance, time, upositive, unegative, bpm, calories, comment)
		self.recordwindow.run()

	def editRecord(self,id_record,list_sport):
		record = self.ddbb.select("records", "*", "id_record=\"%s\"" %id_record)	
		gpxfile = self.conf.getValue("gpxdir")+"/%d.gpx"%int(id_record)
		self.recordwindow = WindowRecord(self.data_path, list_sport,self, None)
		if os.path.isfile(gpxfile):
			self.recordwindow.rcd_gpxfile.set_text(gpxfile)
		self.recordwindow.setValues(record[0])
		self.recordwindow.run()
	
	def removeRecord(self,id_record):
		record = self.ddbb.delete("records", "id_record=\"%s\"" %id_record)
		gpxfile = self.conf.getValue("gpxdir")+"/%d.gpx"%int(id_record)
		if os.path.isfile(gpxfile):
			os.remove(gpxfile)

	def _formatRecord (self, list_options):
		time = self.date.time2second(list_options["rcd_time"])
		average = self.parseFloatRecord(list_options["rcd_average"])
		cells= "date,sport,distance,time,beats,comments,average,calories,title,upositive,unegative"
		if (list_options["rcd_beats"] == ""):
			list_options["rcd_beats"] = 0
		
		#calculate the sport id
		sport_id = self.ddbb.select("sports","id_sports","name=\"%s\"" %list_options["rcd_sport"])[0][0]

		values= (
			list_options["rcd_date"],
			sport_id,
			self.parseFloatRecord(list_options["rcd_distance"]),
			time,
			self.parseFloatRecord(list_options["rcd_beats"]),
			list_options["rcd_comments"],
			average,
			self.parseFloatRecord(list_options["rcd_calories"]),
			list_options["rcd_title"],
			self.parseFloatRecord(list_options["rcd_upositive"]),
			self.parseFloatRecord(list_options["rcd_unegative"])

			)
		return cells,values

	def insertRecord(self, list_options):
		cells,values = self._formatRecord(list_options)
		self.ddbb.insert("records",cells,values)
		gpxOrig = self.conf.tmpdir+"/newgpx.gpx"
		if os.path.isfile(gpxOrig):
			gpxDest = self.conf.getValue("gpxdir")
			id_record = self.ddbb.lastRecord("records")
			shutil.copy2(gpxOrig, gpxDest+"/%d.gpx"%id_record)
		self.parent.refreshListRecords()
		return self.ddbb.lastRecord("records")

	def updateRecord(self, list_options, id_record):
		gpxfile = self.conf.getValue("gpxdir")+"/%d.gpx"%int(id_record)
		if os.path.isfile(list_options["rcd_gpxfile"]):
			if gpxfile != list_options["rcd_gpxfile"]:
				gpxOrig = self.conf.tmpdir+"/newgpx.gpx"
				shutil.copy2(gpxOrig, gpxfile)
		else:
			if (list_options["rcd_gpxfile"]==""):
				print "borrar el gpxfile"
				print "actualizar la bbdd"
		cells,values = self._formatRecord(list_options)
		self.ddbb.update("records",cells,values," id_record=%d" %id_record)
		self.parent.refreshListView()

	def parseFloatRecord(self,string):
		if string != "":
			try:
				return float(string.replace(",",","))
			except:
				return float(string)
		else:
			return 0
				
	def getrecordInfo(self,id_record):
		return self.ddbb.select("records,sports",
					"sports.name,date,distance,time,beats,comments,average,calories,id_record,title,upositive,unegative",
					"id_record=\"%s\" and records.sport=sports.id_sports" %id_record)
	
	def getrecordList(self,date):
		return self.ddbb.select("records,sports",
					"sports.name,date,distance,time,beats,comments,average,calories,id_record",
					"date=\"%s\" and records.sport=sports.id_sports" %date)
	
	def getrecordPeriodSport(self,date_ini, date_end,sport):
		if sport<1 :
			tables = "records"
			condition = "date>\"%s\" and date<\"%s\"" %(date_ini,date_end)
		else :
			tables = "records,sports"
			condition = "date>\"%s\" and date<\"%s\" and records.sport=sports.id_sports and sports.name=\"%s\"" %(date_ini,date_end,sport)
		
		return self.ddbb.select(tables,
					"date,distance,time,beats,comments,average,calories",
					condition)
	
	def getAllrecord(self):
		return self.ddbb.select("records", "date,distance,time,beats,comments,average,calories")
	
	def getAllRecordList(self):
		return self.ddbb.select("records,sports", 
			"date,distance,average,title,sports.name,id_record,time,beats,calories",
			"sports.id_sports = records.sport order by date desc")
	
	def getRecordListByCondition(self,condition):
		return self.ddbb.select("records,sports", 
			"date,distance,average,title,sports.name,id_record,time,beats,calories",
			"sports.id_sports = records.sport and %s" %condition)

	def getRecordDayList(self,date):
		year,month,day = date.split("-")
		records = self.ddbb.select("records","date","date LIKE '"+year+"-"+month+"-%'")
		day_list = []
		for i in records:
			record = i[0].split("-")
			day_list.append(record[2])
		return day_list
		
	def actualize_fromgpx(self,gpxfile):
		gpx = Gpx(self.data_path,gpxfile)
		tracks = gpx.getTrackRoutes()

		if len(tracks) == 1:
			self._actualize_fromgpx(gpxfile)
		elif len(tracks) > 1:
			self._select_trkfromgpx(gpxfile,tracks)
		else:
			msg = _("pyTrainer cant import data from your gpx file")
			from gui.warning import Warning
			warning = Warning(self.data_path)
                        warning.set_text(msg)
                        warning.run()

	def _actualize_fromgpx(self, gpxfile, trkname = None):
		gpx = Gpx(self.data_path,gpxfile,trkname)
		distance, time = gpx.getMaxValues()
		upositive,unegative = gpx.getUnevenness()
		heartrate = gpx.getHeartRateAverage()
		date = gpx.getTrackRoutes()[0][1]
		
		self.recordwindow.rcd_date.set_text(date)
		self.recordwindow.rcd_upositive.set_text(str(upositive))
		self.recordwindow.rcd_unegative.set_text(str(unegative))
		self.recordwindow.rcd_beats.set_text(str(heartrate))
		self.recordwindow.set_distance(distance)
		self.recordwindow.set_recordtime(time/60.0/60.0)
		self.recordwindow.on_calcaverage_clicked(None)

	def _select_trkfromgpx(self,gpxfile,tracks):
		print "seleccionamos el trk"
		selectrckdialog = DialogSelectTrack(self.data_path, tracks,self._actualize_fromgpx, gpxfile)
		selectrckdialog.run()
		
	def newGpxRecord(self,gpxfile,list_sport):
		self.recordwindow = WindowRecord(self.data_path, list_sport,self, None)
		self.recordwindow.rcd_gpxfile.set_text(gpxfile)
		self.actualize_fromgpx(gpxfile)
		self.recordwindow.run()
		
