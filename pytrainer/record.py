# -*- coding: iso-8859-1 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net
#Modified by dgranda

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
import traceback

from gui.windowrecord import WindowRecord
from gui.dialogselecttrack import DialogSelectTrack
from lib.ddbb import DDBB
from lib.xmlUtils import XMLParser
from lib.date import Date
from lib.gpx import Gpx
from pytrainer.equipment import EquipmentService

class Record:
	def __init__(self, data_path = None, parent = None):
		logging.debug('>>')
		self.parent = parent
		self.pytrainer_main = parent
		self._equipment_service = EquipmentService(self.pytrainer_main.ddbb)
		self.data_path = data_path
		logging.debug('setting date...')
		self.date = Date()
		logging.debug('<<')

	def newRecord(self, list_sport, date, title=None, distance=None, time=None, upositive=None, unegative=None, bpm=None, calories=None, comment=None):
		logging.debug('>>')
		self.recordwindow = WindowRecord(self._equipment_service, self.data_path, list_sport,self, date, title, distance, time, upositive, unegative, bpm, calories, comment)
		self.recordwindow.run()
		logging.debug('<<')

	def newMultiRecord(self, activities, list_sport):
		logging.debug('>>')
		#activities (activity_id, start_time, distance, duration, sport, gpx_file)
		self.recordwindow = WindowRecord(self._equipment_service, self._equipment_service, self.data_path, list_sport, parent=self, windowTitle="Modify details before importing")
		self.recordwindow.populateMultiWindow(activities)
		self.recordwindow.run()
		return self.recordwindow.getActivityData()
		logging.debug('<<')

	def editRecord(self,id_record,list_sport):
		logging.debug('>>')
		activity = self.pytrainer_main.activitypool.get_activity(id_record)
		record_equipment = self.get_record_equipment(id_record)
		self.recordwindow = WindowRecord(self._equipment_service, self.data_path, list_sport, self, None, windowTitle=_("Edit Entry"), equipment=record_equipment)
		self.recordwindow.setValuesFromActivity(activity)
		'''
		record = self.pytrainer_main.ddbb.select("records", "id_record, date, sport, distance, time, beats, average, calories, comments, gpslog, title, upositive, unegative, maxspeed, maxpace, pace, maxbeats, date_time_utc, date_time_local", "id_record=\"%s\"" %id_record)
		logging.debug('retrieving data from DB: '+str(record))
		gpxfile = self.pytrainer_main.profile.gpxdir+"/%d.gpx"%int(id_record)
		logging.debug('gpx file associated: '+gpxfile)
		self.recordwindow = WindowRecord(self.data_path, list_sport,self, None, windowTitle=_("Edit Entry"))
		if os.path.isfile(gpxfile):
			self.recordwindow.rcd_gpxfile.set_text(gpxfile)
			self.recordwindow.frameGeneral.set_sensitive(0)		#Currently record values not changed if a GPX file is present
			self.recordwindow.frameVelocity.set_sensitive(0)	#Greying out options to indicate this to user
		logging.debug('sending record info to window')
		self.recordwindow.setValues(record[0])
		'''
		logging.debug('launching window')
		self.recordwindow.run()
		logging.debug('<<')

	def removeRecord(self,id_record):
		logging.debug('>>')
		record = self.pytrainer_main.ddbb.delete("records", "id_record=\"%s\"" %id_record)
		laps = self.pytrainer_main.ddbb.delete("laps", "record=\"%s\"" %id_record)
		logging.debug('removed record '+str(id_record)+' (and associated laps) from DB')
		gpxfile = self.pytrainer_main.profile.gpxdir+"/%d.gpx"%int(id_record)
		if os.path.isfile(gpxfile):
			os.remove(gpxfile)
			logging.debug('removed gpxfile '+gpxfile)
		logging.debug('<<')

	def _formatRecord (self, list_options):
		logging.debug('>>')
		time = self.date.time2second(list_options["rcd_time"])
		average = self.parseFloatRecord(list_options["rcd_average"])
		cells= "date,sport,distance,time,beats,comments,average,calories,title,upositive,unegative,maxspeed,maxpace,pace,maxbeats"
		if (list_options["rcd_beats"] == ""):
			list_options["rcd_beats"] = 0

		#calculate the sport id
		sport_id = self.pytrainer_main.ddbb.select("sports","id_sports","name=\"%s\"" %list_options["rcd_sport"])[0][0]

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
			self.pace_to_float(list_options["rcd_maxpace"]),
			self.pace_to_float(list_options["rcd_pace"]),
			self.parseFloatRecord(list_options["rcd_maxbeats"])
			)
		logging.debug('<<')
		return cells,values

	def pace_to_float(self, value):
		'''Take a mm:ss or mm.ss and return float'''
		value = value.replace(':', '.')
		try:
			value = float(value)
		except ValueError:
			value = None
		return value

	def pace_from_float(self, value):
		'''Helper to generate mm:ss from float representation mm.ss (or mm,ss?)'''
		#Check that value supplied is a float
		try:
			_value = "%0.2f" % float(value)
		except ValueError:
			_value = str(value)
		return _value.replace('.',':')

	def _formatRecordNew (self, list_options):
		"""20.07.2008 - dgranda
		New records handle date_time_utc field which is transparent when updating, so logic method has been splitted
		args: list with keys and values without valid format
		returns: keys and values matching DB schema"""
		logging.debug('>>')
		time = self.date.time2second(list_options["rcd_time"])
		average = self.parseFloatRecord(list_options["rcd_average"])
		keys= "date,sport,distance,time,beats,comments,average,calories,title,upositive,unegative,maxspeed,maxpace,pace,maxbeats,date_time_utc,date_time_local, duration"
		if (list_options["rcd_beats"] == ""):
			list_options["rcd_beats"] = 0

		#retrieving sport id (adding sport if it doesn't exist yet)
		sport_id = self.getSportId(list_options["rcd_sport"],add=True)

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
			self.pace_to_float(list_options["rcd_maxpace"]),
			self.pace_to_float(list_options["rcd_pace"]),
			self.parseFloatRecord(list_options["rcd_maxbeats"]),
			list_options["date_time_utc"],
			list_options["date_time_local"],
			time,
			)
		logging.debug('<<')
		return keys,values

	def insertRecord(self, list_options, laps=None, equipment=None):
		logging.debug('>>')
		#Create entry for activity in records table
		if list_options is None:
			logging.info('No data provided, abort adding entry')
			return None
		logging.debug('list_options: '+str(list_options))
		cells,values = self._formatRecordNew(list_options)
		self.pytrainer_main.ddbb.insert("records",cells,values)
		logging.debug('DB updated: '+str(cells)+' | '+str(values))
		id_record = self.pytrainer_main.ddbb.lastRecord("records")
		#Create entry(s) for activity in laps table
		if laps is not None:
			for lap in laps:
				lap['record'] = id_record #Add reference to entry in record table
				lap_keys = ", ".join(map(str, lap.keys()))
				lap_values = lap.values()
				self.insertLaps(lap_keys,lap.values())
		if equipment is not None:
			for equipment_id in equipment:
				self._insert_record_equipment(id_record, equipment_id)
		gpxOrig = list_options["rcd_gpxfile"]
		if os.path.isfile(gpxOrig):
			gpxDest = self.pytrainer_main.profile.gpxdir
			gpxNew = gpxDest+"/%d.gpx"%id_record
			#Leave original file in place...
			#shutil.move(gpxOrig, gpxNew)
			#logging.debug('Moving '+gpxOrig+' to '+gpxNew)
			shutil.copy(gpxOrig, gpxNew)
			logging.debug('Copying '+gpxOrig+' to '+gpxNew)
		#self.parent.refreshListRecords()
		logging.debug('<<')
		return self.pytrainer_main.ddbb.lastRecord("records")

	def insertNewRecord(self, gpxOrig, entry): #TODO consolidate with insertRecord
		"""29.03.2008 - dgranda
		Moves GPX file to store destination and updates database
		args: path to source GPX file"""
		logging.debug('--')
		(list_options, gpx_laps) = self.summaryFromGPX(gpxOrig, entry)
		if list_options is None:
			return None
		return self.insertRecord(list_options, laps=gpx_laps)

	def lapsFromGPX(self, gpx):
		logging.debug('>>')
		laps = []
		gpxLaps = gpx.getLaps()
		for lap in gpxLaps:
			lap_number = gpxLaps.index(lap)
			tmp_lap = {}
			tmp_lap['record'] = ""
			tmp_lap['lap_number'] = lap_number
			tmp_lap['elapsed_time'] = lap[0]
			tmp_lap['distance'] = lap[4]
			tmp_lap['start_lat'] = lap[5]
			tmp_lap['start_lon'] = lap[6]
			tmp_lap['end_lat'] = lap[1]
			tmp_lap['end_lon'] = lap[2]
			tmp_lap['calories'] = lap[3]
			tmp_lap['intensity'] = lap[7]
			tmp_lap['avg_hr'] = lap[8]
			tmp_lap['max_hr'] = lap[9]
			tmp_lap['max_speed'] = lap[10]
			tmp_lap['trigger'] = lap[11]
			tmp_lap['comments'] = ""
			laps.append(tmp_lap)
		logging.debug('<<')
		return laps

	def summaryFromGPX(self, gpxOrig, entry):
		"""29.03.2008 - dgranda
		Retrieves info which will be stored in DB from GPX file
		args: path to source GPX file
		returns: list with fields and values, list of laps
		"""
		logging.debug('>>')
		gpx = Gpx(self.data_path,gpxOrig)
		distance, time, maxspeed, maxheartrate = gpx.getMaxValues()
		#if time == 0: #invalid record
		#	print "Invalid record"
		#	return (None, None)
		upositive,unegative = gpx.getUnevenness()
		if time > 0:
			speed = distance*3600/time
			time_hhmmss = [time//3600,(time/60)%60,time%60]
		else:
			speed = 0
			time_hhmmss = [0,0,0]
		summaryRecord = {}
		summaryRecord['rcd_gpxfile'] = gpxOrig
		summaryRecord['rcd_sport'] = entry[0]
		summaryRecord['rcd_date'] = gpx.getDate()
		summaryRecord['rcd_calories'] = gpx.getCalories()
		summaryRecord['rcd_comments'] = ''
		summaryRecord['rcd_title'] = ''
		summaryRecord['rcd_time'] = time_hhmmss #ToDo: makes no sense to work with arrays
		summaryRecord['rcd_distance'] = "%0.2f" %distance
		if speed == 0:
			summaryRecord['rcd_pace'] = "0"
		else:
			summaryRecord['rcd_pace'] = "%d.%02d" %((3600/speed)/60,(3600/speed)%60)
		if maxspeed == 0:
			summaryRecord['rcd_maxpace'] = "0"
		else:
			summaryRecord['rcd_maxpace'] = "%d.%02d" %((3600/maxspeed)/60,(3600/maxspeed)%60)
		summaryRecord['rcd_average'] = speed
		summaryRecord['rcd_maxvel'] = maxspeed
		summaryRecord['rcd_beats'] = gpx.getHeartRateAverage()
		summaryRecord['rcd_maxbeats'] = maxheartrate
		summaryRecord['rcd_upositive'] = upositive
		summaryRecord['rcd_unegative'] = unegative
		if entry[1]=="": # coming from new track dialog (file opening)												#TODO This if-else needs checking
			summaryRecord['date_time_utc'], summaryRecord['date_time_local'] = gpx.getStartTimeFromGPX(gpxOrig)		#
		else: # coming from GPS device																				#
			summaryRecord['date_time_utc'] = entry[1]																#
			summaryRecord['date_time_local'] = entry[1]																#
			print "#TODO fix record summaryRecord local and utc time..."											#
		logging.debug('summary: '+str(summaryRecord))
		laps = self.lapsFromGPX(gpx)
		logging.debug('<<')
		return summaryRecord, laps

	def updateRecord(self, list_options, id_record, equipment=None):
		logging.debug('>>')
		#Remove activity from pool so data is updated
		self.pytrainer_main.activitypool.remove_activity(id_record)
		gpxfile = self.pytrainer_main.profile.gpxdir+"/%d.gpx"%int(id_record)
		gpxOrig = list_options["rcd_gpxfile"]
		if os.path.isfile(gpxOrig):
			if gpxfile != gpxOrig:
				shutil.copy2(gpxOrig, gpxfile)
		else:
			if (list_options["rcd_gpxfile"]==""):
				logging.debug('Activity not based in GPX file') # ein?
		logging.debug('Updating bbdd')
		cells,values = self._formatRecordNew(list_options)
		self.pytrainer_main.ddbb.update("records",cells,values," id_record=%d" %int(id_record))
		if equipment is not None:
			self._update_record_equipment(id_record, equipment)
		self.pytrainer_main.refreshListView()
		logging.debug('<<')

	def parseFloatRecord(self,string):
		logging.debug('--')
		if string != "":
			try:
				return float(string.replace(",",","))
			except:
				return float(string)
		else:
			return 0

	def getrecordInfo(self,id_record):
		logging.debug('--')
		if id_record is None or id_record == "":
			return []
		return self.pytrainer_main.ddbb.select("records,sports",
					"sports.name,date,distance,time,beats,comments,average,calories,id_record,title,upositive,unegative,maxspeed,maxpace,pace,maxbeats,date_time_utc,date_time_local",
					"id_record=\"%s\" and records.sport=sports.id_sports" %id_record)

	def getrecordList(self,date, id_sport=None):
		logging.debug('--')
		if not id_sport:
			return self.pytrainer_main.ddbb.select("records,sports",
					"sports.name,date,distance,time,beats,comments,average,calories,id_record,maxspeed,maxbeats,date_time_utc,date_time_local,upositive,unegative",
					"date=\"%s\" and records.sport=sports.id_sports" %date)
		else:
			return self.pytrainer_main.ddbb.select("records,sports",
					"sports.name,date,distance,time,beats,comments,average,calories,id_record,maxspeed,maxbeats,date_time_utc,date_time_local,upositive,unegative",
					"date=\"%s\" and sports.id_sports=\"%s\" and records.sport=sports.id_sports" %(date,id_sport))

	def getLaps(self, id_record):
		logging.debug('--')
		laps = self.pytrainer_main.ddbb.select("laps",
					"id_lap, record, elapsed_time, distance, start_lat, start_lon, end_lat, end_lon, calories, lap_number, intensity, max_speed, avg_hr, max_hr, laptrigger, comments",
					"record=\"%s\"" % id_record)
		if laps is None or laps == []:  #No laps stored - update DB
			logging.debug("No laps in DB for record %d" % id_record)
			#print ("No laps in DB for record %d" % id_record)
			gpx_dest = self.pytrainer_main.profile.gpxdir
			gpxfile = gpx_dest+"/%d.gpx"%id_record
			gpx = Gpx(self.data_path,gpxfile)
			laps = self.lapsFromGPX(gpx)
			if laps is not None:
				for lap in laps:
					lap['record'] = id_record #Add reference to entry in record table
					lap_keys = ", ".join(map(str, lap.keys()))
					lap_values = lap.values()
					self.insertLaps(lap_keys,lap.values())
			#Try to get lap info again #TODO? refactor
			laps = self.pytrainer_main.ddbb.select("laps",
					"id_lap, record, elapsed_time, distance, start_lat, start_lon, end_lat, end_lon, calories, lap_number, intensity, max_speed, avg_hr, max_hr, laptrigger, comments",
					"record=\"%s\"" % id_record)
		return laps

	def insertLaps(self, cells, values):
		logging.debug('--')
		logging.debug("Adding lap information: " + ", ".join(map(str, values)))
		self.pytrainer_main.ddbb.insert("laps",cells,values)
		
	def _insert_record_equipment(self, record_id, equipment_id):
		self.pytrainer_main.ddbb.insert("record_equipment", "record_id, equipment_id", [record_id, equipment_id])
		
	def _update_record_equipment(self, record_id, equipment_ids):
		self.pytrainer_main.ddbb.delete("record_equipment", "record_id={0}".format(record_id))
		for id in equipment_ids:
			self._insert_record_equipment(record_id, id)
			
	def get_record_equipment(self, record_id):
		record_equipment = []
		results = self.pytrainer_main.ddbb.select("record_equipment", "equipment_id", "record_id={0}".format(record_id))
		for row in results:
			id = row[0]
			equipment_item = self._equipment_service.get_equipment_item(id)
			record_equipment.append(equipment_item)
		return record_equipment

	def getrecordPeriod(self,date_ini, date_end, sport=None):
		#TODO This is essentially the same as getrecordPeriodSport (except date ranges) - need to look at merging the two
		tables = "records,sports"
		if not sport:
			condition = "date>=\"%s\" and date<\"%s\" and records.sport=sports.id_sports" %(date_ini,date_end)
		else:
			condition = "date>=\"%s\" and date<\"%s\" and records.sport=sports.id_sports and sports.id_sports=\"%s\"" %(date_ini,date_end, sport)

		return self.pytrainer_main.ddbb.select(tables,"date,distance,time,beats,comments,average,calories,maxspeed,maxbeats, sports.name,upositive,unegative", condition)

	def getrecordPeriodSport(self,date_ini, date_end,sport):
		if not sport:
			tables = "records"
			condition = "date>\"%s\" and date<\"%s\"" %(date_ini,date_end)
		else :
			tables = "records,sports"
			condition = "date>\"%s\" and date<\"%s\" and records.sport=sports.id_sports and sports.id_sports=\"%s\"" %(date_ini,date_end,sport)

		return self.pytrainer_main.ddbb.select(tables,
					"date,distance,time,beats,comments,average,calories,maxspeed,maxbeats,upositive,unegative",
					condition)

	def getSportMet(self,sport):
		logging.debug('--')
		return self.pytrainer_main.ddbb.select("sports","met","name=\"%s\"" %(sport))[0][0]

	def getSportWeight(self,sport):
		logging.debug('--')
		return self.pytrainer_main.ddbb.select("sports","weight","name=\"%s\"" %(sport))[0][0]

	def getSportId(self,sport,add=None):
		"""31.08.2008 - dgranda
		Retrieves id_sports from provided sport. If add is not set to None, sport is added to the system
		arguments:
			sport: sport's name to get id from
			add: attribute to add or not the sport to db
		returns: id_sports from provided sport"""
		logging.debug('>>')
		sport_id=None
		if sport == "" or sport is None:
			return sport_id
		try:
			sport_id = self.pytrainer_main.ddbb.select("sports","id_sports","name=\"%s\"" %(sport))[0][0]
		except:
			logging.error('Error retrieving id_sports from '+ str(sport))
			#traceback.print_last()
			if add is None:
				logging.debug('Sport '+str(sport)+' will not be added to DB')
			else:
				logging.debug('Adding sport '+str(sport)+' to DB')
				sport_id = self.addNewSport(sport,"0","0")
		logging.debug('<<')
		return sport_id

	def addNewSport(self,sport,met,weight):
		"""31.08.2008 - dgranda
		Copied from Profile class, adds a new sport.
		arguments:
			sport: sport's name
			met:
			weight:
		returns: id_sports from new sport"""
		logging.debug(">>")
		logging.debug("Adding new sport: "+sport+"|"+weight+"|"+met)
		sportT = [sport,met,weight]
		self.pytrainer_main.ddbb.insert("sports","name,met,weight",sportT)
		sport_id = self.pytrainer_main.ddbb.select("sports","id_sports","name=\"%s\"" %(sport))[0][0]
		logging.debug("<<")
		return sport_id

	def getAllrecord(self):
		logging.debug('--')
		return self.pytrainer_main.ddbb.select("records", "date,distance,time,beats,comments,average,calories")

	def getAllRecordList(self):
		logging.debug('--')
		return self.pytrainer_main.ddbb.select("records,sports",
			"date,distance,average,title,sports.name,id_record,time,beats,calories",
			"sports.id_sports = records.sport order by date desc")

	def getRecordListByCondition(self,condition):
		logging.debug('--')
		if condition is None:
			return self.getAllRecordList()
		else:
			logging.debug("condition: %s" % condition)
			return self.pytrainer_main.ddbb.select("records,sports",
				"date,distance,average,title,sports.name,id_record,time,beats,calories",
				"sports.id_sports = records.sport and %s order by date desc" %condition)

	def getRecordDayList(self,date, id_sport=None):
		logging.debug('>>')
		year,month,day = date.split("-")
		logging.debug('Retrieving data for '+year+'.'+month+'.'+day)
		# Why is looking for all days of the same month?
		if not id_sport:
			records = self.pytrainer_main.ddbb.select("records","date","date LIKE '"+year+"-"+month+"-%'")
		else:
			records = self.pytrainer_main.ddbb.select("records","date","date LIKE \"%s-%s-%%\" and sport=\"%s\"" %(year,month,id_sport))
		logging.debug('Found '+str(len(records))+' entries')
		day_list = []
		for i in records:
			record = str(i[0]).split("-")
			logging.debug('date:'+str(i[0]))
			day_list.append(record[2])
		logging.debug('<<')
		return day_list

	def actualize_fromgpx(self,gpxfile): #TODO remove? - should never have multiple tracks per GPX file
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
			msg = _("pyTrainer can't import data from your gpx file")
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
		calories = gpx.getCalories()

		self.recordwindow.rcd_date.set_text(date)
		self.recordwindow.rcd_upositive.set_text(str(upositive))
		self.recordwindow.rcd_unegative.set_text(str(unegative))
		self.recordwindow.rcd_beats.set_text(str(heartrate))
		self.recordwindow.rcd_calories.set_text(str(calories))
		self.recordwindow.set_distance(distance)
		self.recordwindow.set_maxspeed(maxspeed)
		self.recordwindow.set_maxhr(maxheartrate)
		self.recordwindow.set_recordtime(time/60.0/60.0)
		self.recordwindow.on_calcaverage_clicked(None)
		self.recordwindow.on_calcpace_clicked(None)
		self.recordwindow.on_calccalories_clicked(None)
		self.recordwindow.rcd_maxpace.set_text("%d.%02d" %((3600/maxspeed)/60,(3600/maxspeed)%60))
		logging.debug('<<')

	def __actualize_fromgpx(self, gpxfile, name=None):
		logging.debug('>>')
		gpx = Gpx(self.data_path,gpxfile,name)
		self._actualize_fromgpx(gpx)
		logging.debug('<<')

	def _select_trkfromgpx(self,gpxfile,tracks):  #TODO remove? - should never have multiple tracks per GPX file
		logging.debug('>>')
		logging.debug('Track dialog '+ self.data_path +'|'+ gpxfile)
		selectrckdialog = DialogSelectTrack(self.data_path, tracks,self.__actualize_fromgpx, gpxfile)
		logging.debug('Launching window...')
		selectrckdialog.run()
		logging.debug('<<')

	def newGpxRecord(self,gpxfile,list_sport): #TODO Not used?
		logging.debug('>>')
		logging.debug("opening a new window record "+self.data_path+'|'+gpxfile+'|'+str(list_sport))
		self.recordwindow = WindowRecord(self._equipment_service, self.data_path, list_sport,self, None)
		logging.debug('setting text in window '+ gpxfile)
		self.recordwindow.rcd_gpxfile.set_text(gpxfile)
		logging.debug('retrieving data from gpx file')
		self.actualize_fromgpx(gpxfile)
		logging.debug('Launching window...')
		self.recordwindow.run()
		logging.debug('<<')

	def importFromGPX(self, gpxFile, sport):
		"""
		Add a record from a valid pytrainer type GPX file
		"""
		logging.debug('>>')
		entry_id = None
		if not os.path.isfile(gpxFile):
			logging.error("Invalid file: " +gpxFile)
		else:
			logging.info('Retrieving data from '+gpxFile)
			if not sport:
				sport = "import"
			entry = [sport,""]
			entry_id = self.insertNewRecord(gpxFile, entry)
			if entry_id is None:
				logging.error("Entry not created for file %s" % gpxFile)
			else:
				logging.info("Entry %d has been added" % entry_id)
		logging.debug('<<')
		return entry_id
