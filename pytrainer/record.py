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
import logging

from gui.windowrecord import WindowRecord
from gui.dialogselecttrack import DialogSelectTrack
from lib.ddbb import DDBB
from lib.xmlUtils import XMLParser
from lib.system import checkConf
from lib.date import Date
from lib.gpx import Gpx

class Record:
	def __init__(self, data_path = None, parent = None, version=None):
		logging.debug('>>') 
		self.parent = parent
		self.data_path = data_path
		logging.debug('setting date...')
		self.date = Date()
		logging.debug('checking configuration...')
		self.conf = checkConf()
		self.filename = self.conf.getValue("conffile")
		logging.debug('retrieving data from '+ self.filename)
		self.configuration = XMLParser(self.filename)
		self.ddbb = DDBB(self.configuration)
		logging.debug('connecting to DDBB')
		self.ddbb.connect()
		#hack for pytrainer 0.9.5 and previous
		version_tmp = self.configuration.getOption("version")
		logging.debug('version_tmp: '+ version_tmp)
		if version_tmp=="1.0":
			logging.debug('updating month data')
			self.ddbb.updatemonth()
		if version_tmp<="0.9.8":
			logging.debug('updating date format')
			self.ddbb.updateDateFormat()
		if version_tmp<="0.9.8.2":
			logging.debug('updating DB title')
			self.ddbb.addTitle2ddbb()
		if version_tmp<="1.3.1":
			self.ddbb.addUnevenness2ddbb()
		if version_tmp<="1.4.1.1":
			self.ddbb.addWaypoints2ddbb()
		if version_tmp<="1.4.2":
			try:
				self.ddbb.addWaypoints2ddbb()
			except:
				pass
		if version_tmp<="1.5.0":
			self.ddbb.addweightandmet2ddbb()
		if version_tmp<="1.5.0.1":
			self.ddbb.checkmettable()
		if version_tmp<="1.5.0.2":
			self.ddbb.addpaceandmax2ddbb()
		if version_tmp<version:
			self.configuration.setVersion(version)
		logging.debug('<<')

	def newRecord(self, list_sport, date, title=None, distance=None, time=None, upositive=None, unegative=None, bpm=None, calories=None, comment=None):
		self.recordwindow = WindowRecord(self.data_path, list_sport,self, date, title, distance, time, upositive, unegative, bpm, calories, comment)
		self.recordwindow.run()
		logging.debug('<<')

	def editRecord(self,id_record,list_sport):
		logging.debug('>>')
		record = self.ddbb.select("records", "*", "id_record=\"%s\"" %id_record)
		logging.debug('retrieving data from DB: '+str(record))
		gpxfile = self.conf.getValue("gpxdir")+"/%d.gpx"%int(id_record)
		logging.debug('gpx file associated: '+gpxfile)
		self.recordwindow = WindowRecord(self.data_path, list_sport,self, None)
		if os.path.isfile(gpxfile):
			self.recordwindow.rcd_gpxfile.set_text(gpxfile)
		logging.debug('sending record info to window')
		self.recordwindow.setValues(record[0])
		logging.debug('launching window')
		self.recordwindow.run()
		logging.debug('<<')
	
	def removeRecord(self,id_record):
		logging.debug('>>')
		record = self.ddbb.delete("records", "id_record=\"%s\"" %id_record)
		logging.debug('removed record '+str(id_record)+' from bbdd')
		gpxfile = self.conf.getValue("gpxdir")+"/%d.gpx"%int(id_record)
		if os.path.isfile(gpxfile):
			os.remove(gpxfile)
			logging.debug('removed gpxfile '+gpxfile)

	def _formatRecord (self, list_options):
		logging.debug('>>')
		time = self.date.time2second(list_options["rcd_time"])
		average = self.parseFloatRecord(list_options["rcd_average"])
		cells= "date,sport,distance,time,beats,comments,average,calories,title,upositive,unegative,maxspeed,maxpace,pace,maxbeats"
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
			self.parseFloatRecord(list_options["rcd_unegative"]),
			self.parseFloatRecord(list_options["rcd_maxvel"]),
			self.parseFloatRecord(list_options["rcd_maxpace"]),
			self.parseFloatRecord(list_options["rcd_pace"]),
			self.parseFloatRecord(list_options["rcd_maxbeats"])

			)
		logging.debug('<<')
		return cells,values

	def insertRecord(self, list_options):
		logging.debug('>>')
		logging.debug('list_options: '+str(list_options))
		cells,values = self._formatRecord(list_options)
		self.ddbb.insert("records",cells,values)
		logging.debug('DB updated: '+str(cells)+' | '+str(values))
		gpxOrig = self.conf.tmpdir+"/newgpx.gpx"
		if os.path.isfile(gpxOrig):
			gpxDest = self.conf.getValue("gpxdir")
			id_record = self.ddbb.lastRecord("records")
			shutil.copy2(gpxOrig, gpxDest+"/%d.gpx"%id_record)
			logging.debug('Moving '+gpxOrig+' to '+gpxDest+"/"+str(id_record))
		#self.parent.refreshListRecords()
		logging.debug('<<')
		return self.ddbb.lastRecord("records")
		
	def insertNewRecord(self, gpxOrig):
		"""29.03.2008 - dgranda
		Moves GPX file to store destination and updates database
		args: path to source GPX file"""
		logging.debug('--')
		return self.insertRecord(self.summaryFromGPX(gpxOrig))
		
	def summaryFromGPX(self, gpxOrig):
		"""29.03.2008 - dgranda
		Retrieves info which will be stored in DB from GPX file
		args: path to source GPX file
		returns: list with fields and values"""
		logging.debug('>>')
		gpx = Gpx(self.data_path,gpxOrig)
		distance, time, maxspeed, maxheartrate = gpx.getMaxValues()
		upositive,unegative = gpx.getUnevenness()
		speed = distance*3600/time
		time_hhmmss = [time//3600,(time/60)%60,time%60]
		summaryRecord = {}
		summaryRecord['rcd_gpxfile'] = gpxOrig
		summaryRecord['rcd_sport'] = 'Run' # hardcoded
		summaryRecord['rcd_date'] = gpx.getDate()
		summaryRecord['rcd_calories'] = '0.0' # not supported yet (29.03.2008)
		summaryRecord['rcd_comments'] = ''
		summaryRecord['rcd_title'] = ''
		summaryRecord['rcd_time'] = time_hhmmss #ToDo: makes no sense to work with arrays
		summaryRecord['rcd_distance'] = "%0.2f" %distance 
		summaryRecord['rcd_pace'] = "%0.2f" %(60/speed) #not in right format (4:90!!!)
		summaryRecord['rcd_maxpace'] = "%0.2f" %(60/maxspeed) #not in right format (4:90!!!)
		summaryRecord['rcd_average'] = speed
		summaryRecord['rcd_maxvel'] = maxspeed
		summaryRecord['rcd_beats'] = gpx.getHeartRateAverage()
		summaryRecord['rcd_maxbeats'] = maxheartrate
		summaryRecord['rcd_upositive'] = upositive
		summaryRecord['rcd_unegative'] = unegative
		logging.debug('summary: '+str(summaryRecord))
		logging.debug('<<')
		return summaryRecord

	def updateRecord(self, list_options, id_record):
		logging.debug('>>')
		gpxfile = self.conf.getValue("gpxdir")+"/%d.gpx"%int(id_record)
		if os.path.isfile(list_options["rcd_gpxfile"]):
			if gpxfile != list_options["rcd_gpxfile"]:
				gpxOrig = self.conf.tmpdir+"/newgpx.gpx"
				shutil.copy2(gpxOrig, gpxfile)
		else:
			if (list_options["rcd_gpxfile"]==""):
				logging.debug('removing gpxfile') # ein?
				logging.debug('updating bbdd') #ein?
		cells,values = self._formatRecord(list_options)
		self.ddbb.update("records",cells,values," id_record=%d" %id_record)
		self.parent.refreshListView()
		logging.debug('<<')

	def parseFloatRecord(self,string):
		logging.debug('>>')
		if string != "":
			try:
				return float(string.replace(",",","))
			except:
				return float(string)
		else:
			return 0
				
	def getrecordInfo(self,id_record):
		logging.debug('--')
		return self.ddbb.select("records,sports",
					"sports.name,date,distance,time,beats,comments,average,calories,id_record,title,upositive,unegative,maxspeed,maxpace,pace,maxbeats",
					"id_record=\"%s\" and records.sport=sports.id_sports" %id_record)
	
	def getrecordList(self,date):
		logging.debug('--')
		return self.ddbb.select("records,sports",
					"sports.name,date,distance,time,beats,comments,average,calories,id_record,maxspeed,maxbeats",
					"date=\"%s\" and records.sport=sports.id_sports" %date)
	
	def getrecordPeriodSport(self,date_ini, date_end,sport):
		if sport<1 :
			tables = "records"
			condition = "date>\"%s\" and date<\"%s\"" %(date_ini,date_end)
		else :
			tables = "records,sports"
			condition = "date>\"%s\" and date<\"%s\" and records.sport=sports.id_sports and sports.name=\"%s\"" %(date_ini,date_end,sport)
		
		return self.ddbb.select(tables,
					"date,distance,time,beats,comments,average,calories,maxspeed,maxbeats",
					condition)

	def getSportMet(self,sport):
		logging.debug('--')
		return self.ddbb.select("sports","met","name=\"%s\"" %(sport))[0][0]
	
	def getSportWeight(self,sport):
		logging.debug('--')
		return self.ddbb.select("sports","weight","name=\"%s\"" %(sport))[0][0]
	
	def getAllrecord(self):
		logging.debug('--')
		return self.ddbb.select("records", "date,distance,time,beats,comments,average,calories")
	
	def getAllRecordList(self):
		logging.debug('--')
		return self.ddbb.select("records,sports", 
			"date,distance,average,title,sports.name,id_record,time,beats,calories",
			"sports.id_sports = records.sport order by date desc")
	
	def getRecordListByCondition(self,condition):
		logging.debug('--')
		return self.ddbb.select("records,sports", 
			"date,distance,average,title,sports.name,id_record,time,beats,calories",
			"sports.id_sports = records.sport and %s" %condition)

	def getRecordDayList(self,date):
		logging.debug('>>')
		year,month,day = date.split("-")
		logging.debug('Retrieving data for '+year+'.'+month+'.'+day)
		# Why is looking for all days of the same month?
		records = self.ddbb.select("records","date","date LIKE '"+year+"-"+month+"-%'")
		logging.debug('Found '+str(len(records))+' entries')
		day_list = []
		for i in records:
			record = i[0].split("-")
			logging.debug('date:'+i[0])
			day_list.append(record[2])
		logging.debug('<<')
		return day_list
		
	def actualize_fromgpx(self,gpxfile):
		logging.debug('>>')
		logging.debug('loading file: '+gpxfile)
		gpx = Gpx(self.data_path,gpxfile)
		tracks = gpx.getTrackRoutes()

		if len(tracks) == 1:
			logging.debug('Just 1 track')
			self._actualize_fromgpx(gpx)
		elif len(tracks) > 1:
			logging.debug('Found '+str(len(tracks))+' tracks')
			self._select_trkfromgpx(gpxfile,tracks)
		else:
			msg = _("pyTrainer cant import data from your gpx file")
			from gui.warning import Warning
			warning = Warning(self.data_path)
			warning.set_text(msg)
			warning.run()
		logging.debug('<<')

	def _actualize_fromgpx(self, gpx):
		logging.debug('>>')
		distance, time, maxspeed, maxheartrate = gpx.getMaxValues()
		upositive,unegative = gpx.getUnevenness()
		heartrate = gpx.getHeartRateAverage()
		date = gpx.getDate()
		
		self.recordwindow.rcd_date.set_text(date)
		self.recordwindow.rcd_upositive.set_text(str(upositive))
		self.recordwindow.rcd_unegative.set_text(str(unegative))
		self.recordwindow.rcd_beats.set_text(str(heartrate))
		self.recordwindow.set_distance(distance)
		self.recordwindow.set_maxspeed(maxspeed)
		self.recordwindow.set_maxhr(maxheartrate)
		self.recordwindow.set_recordtime(time/60.0/60.0)
		self.recordwindow.on_calcaverage_clicked(None)
		self.recordwindow.on_calcpace_clicked(None)
		self.recordwindow.on_calccalories_clicked(None)
		self.recordwindow.rcd_maxpace.set_text("%0.2f" %(60/maxspeed))
		logging.debug('<<')
	
	def __actualize_fromgpx(self, gpxfile, name=None):
		logging.debug('>>')
		gpx = Gpx(self.data_path,gpxfile,name)
		self._actualize_fromgpx(gpx)
		logging.debug('<<')

	def _select_trkfromgpx(self,gpxfile,tracks):
		logging.debug('>>')
		logging.debug('Track dialog '+ self.data_path +'|'+ gpxfile)
		selectrckdialog = DialogSelectTrack(self.data_path, tracks,self.__actualize_fromgpx, gpxfile)
		logging.debug('Launching window...')
		selectrckdialog.run()
		logging.debug('<<')
		
	def newGpxRecord(self,gpxfile,list_sport):
		logging.debug('>>')
		logging.debug("opening a new window record "+self.data_path+'|'+gpxfile+'|'+str(list_sport))
		self.recordwindow = WindowRecord(self.data_path, list_sport,self, None)
		logging.debug('setting text in window '+ gpxfile)
		self.recordwindow.rcd_gpxfile.set_text(gpxfile)
		logging.debug('retrieving data from gpx file')
		self.actualize_fromgpx(gpxfile)
		logging.debug('Launching window...')
		self.recordwindow.run()
		logging.debug('<<')

	def importFromGTRNCTR(self,gtrnctrFile):
		"""22.03.2008 - dgranda
		Retrieves sport, date and start time from each entry coming from GPS
		and compares with is stored locally, just to import new entries
		args: file with data from GPS file (garmin format)
		returns: list with dictionaries: SPORT|DATE|START_TIME"""
		logging.debug('>>')
		logging.info('Retrieving data from '+gtrnctrFile)
		xmlParser=XMLParser(gtrnctrFile)
		listTracksGPS = xmlParser.shortFromGPS(gtrnctrFile) # Done 22.03.2008
		logging.info('GPS: '+str(len(listTracksGPS))+' entries found')
		# ToDo: store this info in DB for each record -> implies DB schema changes
		if len(listTracksGPS)>0:
			listTracksLocal = self.shortFromLocal() # Done 25.03.2008
			logging.info('Local: '+str(len(listTracksLocal))+' entries found')
			listNewTracks=self.compareTracks(listTracksGPS,listTracksLocal) # Done 22.03.2008
			newTracks = len(listNewTracks)
			#un nuevo constructor vacío para Gpx 
			gpx = Gpx()
			i=0
			for entry in listNewTracks:
				i=i+1
				logging.debug('Entry summary to import: '+str(entry))
				newGPX=gpx.retrieveDataFromGTRNCTR(gtrnctrFile, entry) # Done 24.03.2008
				entry_id = self.insertNewRecord(newGPX)
				logging.info('Entry '+str(entry_id)+' has been added ('+str(i)+'/'+str(newTracks)+')')
		else:
			logging.info('No tracks found in GPS device')
		logging.debug('<<')
		
	def shortFromLocal(self):
		"""25.03.2008 - dgranda
		Retrieves sport, date and start time from each entry stored locally
		returns: list with dictionaries: SPORT|DATE_START_TIME"""
		logging.debug('>>')
		listTracksGPX = []
		sport = "Run" #hardcoded - 25.03.2008
		# looking in configuration for storing directory
		gpxDir = self.conf.getValue("gpxdir")
		# retrieving how many files are there
		for gpxFile in os.listdir(gpxDir):
			#logging.debug('File: '+gpxFile)
			gpx = Gpx()
			date_time = gpx.getStartTimeFromGPX(gpxDir+"/"+gpxFile)
			logging.debug('File: '+gpxFile+' | Date: '+date_time)
			listTracksGPX.append((sport,date_time))
		logging.debug('<<')
		return listTracksGPX
		
	def compareTracks(self,listTracksGPS,listTracksLocal):
		"""22.03.2008 - dgranda
		Compares tracks retrieved from GPS with already locally stored
		args: lists with dictionaries: SPORT|DATE|START_TIME
		returns: tracks which are not present locally (list with dictionaries)"""
		logging.debug('>>')
		# Optimizing comparison - 26042008
		# http://mail.python.org/pipermail/python-list/2002-May/142854.html
		tempDict = dict(zip(listTracksLocal,listTracksLocal))
		resultList = [x for x in listTracksGPS if x not in tempDict]
		logging.info('Tracks to be imported: '+str(len(resultList)))
		logging.debug('<<')
		return resultList
		
