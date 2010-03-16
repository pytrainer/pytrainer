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
import logging
import gtk, gobject
from SimpleGladeApp import SimpleGladeApp
from windowcalendar import WindowCalendar
from filechooser import FileChooser
from pytrainer.lib.date import Date
import dateutil.parser
from dateutil.tz import * # for tzutc()

class WindowRecord(SimpleGladeApp):
	def __init__(self, data_path = None, listSport = None, parent = None, date = None, title=None, distance=None, time=None, upositive=None, unegative=None, bpm=None, calories=None, comment=None, windowTitle=None):
		self.parent = parent
		self.data_path = data_path
		glade_path="glade/newrecord.glade"
		root = "newrecord"
		domain = None
		self.mode = "newrecord"
		self.id_record = ""
		self.store = None
		self.active_row = None
		self.activity_data = [] 
		SimpleGladeApp.__init__(self, data_path+glade_path, root, domain)
		self.conf_options = [
			"rcd_date",
			"rcd_sport",
			"rcd_distance",
			"rcd_beats",
			"rcd_comments",
			"rcd_average",
			"rcd_calories",
			"rcd_title",
			"rcd_gpxfile",
			"rcd_upositive",
			"rcd_unegative",
			"rcd_maxbeats",
			"rcd_pace",
			"rcd_maxpace",
			"rcd_maxvel",
			]
		self.listSport = {}
		for i in listSport:
			self.listSport[i[3]] = i[0] #Create dictionary using SportID as key (may be non sequential if sports have been deleted)
		for i in self.listSport:	
			self.rcd_sport.insert_text(i,self.listSport[i])
		self.rcd_sport.set_active(0)

		if windowTitle is not None:
			self.newrecord.set_title(windowTitle)
		if date != None:
			self.setDate(date)
		if title != None:
			self.rcd_title.set_text(title)
		if distance != None:
			self.rcd_distance.set_text(distance)
		if time != None:
			self.setTime(time)
		if distance!=None and time!=None:
			self.on_calcaverage_clicked(None)
		if upositive != None:
			self.rcd_upositive.set_text(upositive)
		if unegative != None:
			self.rcd_unegative.set_text(unegative)
		if calories != None:
			self.rcd_calories.set_text(calories)
			
	def getActivityData(self):
		return self.activity_data
		
	def populateMultiWindow(self, activities):
		self.mode = "multiple_activities"
		#activities (activity_id, start_time, distance, duration, sport, gpx_file, file_id)
		self.activity_data = []
		#Make treeview
		self.store = self.build_tree_view()
		#Add data
		for activity in activities:
			iter = self.store.append()
			self.store.set(
					iter,
					0, activity[0],
					1, activity[1],
					2, activity[2],
					3, activity[3],
					4, activity[4],
					5, activity[5]
					)
			details = {}
			details["complete"]  = False
			details["rcd_distance"] = activity[2]
			duration = activity[3]
			if duration.count(":") == 2:
				hours, mins, secs = duration.split(":")
			else:
				hours = mins = secs = 0
			#details["rcd_hour"] = float(hours)
			#details["rcd_min"] = float(mins)
			#details["rcd_second"] = float(secs)
			#details["rcd_time"] = (((float(hours) * 60) + float(mins)) * 60) + float(secs)
			details["activity_id"] = activity[0]
			details["rcd_time"] = (float(hours), float(mins), float(secs))
			details["rcd_sport"] = activity[4]
			details["rcd_gpxfile"] = activity[5]
			details["file_id"] = activity[6]
			self.activity_data.append(details)
		self.scrolledwindowEntries.show_all()
		#Hide some of the buttons
		self.button25.hide() #GPX file "Open" button
		self.button24.hide() #GPX file "Calculate Values" button
		self.button10.hide() #Distance "Calculate" button
		self.button11.hide() #Duration "Calculate" button
		#self.button12.hide() #Velocity "Calculate" button
		self.button43.hide() #Pace "Calculate" button
		#Make GPX file 'unsensitive'
		self.rcd_gpxfile.set_sensitive(0)		
		while gtk.events_pending():	# This allows the GUI to update 
			gtk.main_iteration()	# before completion of this entire action
		#Select first row and display details
		self.treeviewEntries.set_cursor(0)
		self.show_treeviewEntries_row(0)
		
	def build_tree_view(self):
		store = gtk.ListStore(	gobject.TYPE_STRING,
								gobject.TYPE_STRING,
								gobject.TYPE_STRING,
								gobject.TYPE_STRING, 
								gobject.TYPE_STRING, 
								gobject.TYPE_STRING )
		column_names=["id", _("Start Time"), _("Distance"),_("Duration"),_("Sport"), _("GPX File")]
		for column_index, column_name in enumerate(column_names):
			#Add columns
			column = gtk.TreeViewColumn(column_name, gtk.CellRendererText(), text=column_index)
			column.set_sort_column_id(column_index)
			#if column_name == "id":
			#	column.set_visible(False)
			column.set_resizable(True)
			self.treeviewEntries.append_column(column)
		self.treeviewEntries.set_headers_clickable(True)
		self.treeviewEntries.set_model(store)
		return store
		
	def on_accept_clicked(self,widget):
		if self.mode == "multiple_activities":
			#Check for edited data in comments
			if self.active_row is not None:
				buffer = self.rcd_comments.get_buffer()
				start,end = buffer.get_bounds()
				comments = buffer.get_text(start,end, True).replace("\"","'")
				self.activity_data[self.active_row]["rcd_comments"] = comments
				#Advanced tab items
				self.activity_data[self.active_row]["rcd_maxpace"] = self.rcd_maxpace.get_text()
				self.activity_data[self.active_row]["rcd_pace"] = self.rcd_pace.get_text()
				self.activity_data[self.active_row]["rcd_upositive"] = self.rcd_upositive.get_text()
				self.activity_data[self.active_row]["rcd_unegative"] = self.rcd_unegative.get_text()
				self.activity_data[self.active_row]["rcd_maxbeats"] = self.rcd_maxbeats.get_text()
				self.activity_data[self.active_row]["rcd_beats"] = self.rcd_beats.get_text()
				self.activity_data[self.active_row]["rcd_calories"] = self.rcd_calories.get_text()
			row = 0 
			for activity in self.activity_data:
				index = self.activity_data.index(activity)
				if activity["complete"] is False:
					#Did not view or modify this record - need to get all the details
					print "Activity incomplete.. " + activity["rcd_gpxfile"]
					self.update_activity_data(row, activity["rcd_gpxfile"], activity["rcd_sport"])
				activity["rcd_title"] = activity["rcd_title"].replace("\"","'")
				#Add activity to DB etc
				laps = activity.pop("laps", ())
				self.activity_data[index]["db_id"] = self.parent.insertRecord(activity, laps)
				row += 1
			logging.debug("Processed %d rows of activity data" % row)
		else:
			list_options = {}
			trackSummary = {}
			for i in self.conf_options:
				var = getattr(self,i)
				if i == "rcd_title":
					list_options[i] = var.get_text().replace("\"","'")
				elif i != "rcd_sport" and i != "rcd_comments":
					list_options[i] = var.get_text()
				elif i == "rcd_sport":
					list_options[i] = var.get_active_text()
				elif i == "rcd_comments":
					buffer = var.get_buffer()
					start,end = buffer.get_bounds()
					list_options[i] = buffer.get_text(start,end, True)
					list_options[i] = list_options[i].replace("\"","'")
				list_options["rcd_time"] = [self.rcd_hour.get_value_as_int(),self.rcd_min.get_value_as_int(),self.rcd_second.get_value_as_int()]
			if self.mode == "newrecord":
				logging.debug('Track data: '+str(list_options))
				if list_options["rcd_gpxfile"] != "":
					logging.info('Adding new activity based on GPX file')	
					trackSummary=(list_options["rcd_sport"],"","")
					self.parent.insertNewRecord(list_options["rcd_gpxfile"], trackSummary)
				else:
					logging.info('Adding new activity based on provided data')
					#Manual entry, calculate time info
					record_time = self.rcd_starttime.get_text()
					record_date = self.rcd_date.get_text()
					localtz = Date().getLocalTZ()
					date = dateutil.parser.parse(record_date+" "+record_time+" "+localtz)
					local_date = str(date)
					utc_date = date.astimezone(tzutc()).strftime("%Y-%m-%dT%H:%M:%SZ")
					list_options["date_time_utc"] = utc_date
					list_options["date_time_local"] = local_date
					self.parent.insertRecord(list_options)
			elif self.mode == "editrecord":
				self.parent.updateRecord(list_options, self.id_record)
		self.close_window()
	
	def on_cancel_clicked(self,widget):
		self.close_window()

	def close_window(self, widget=None):
		self.newrecord.hide()
		#self.newrecord = None
		self.quit()

	def on_calendar_clicked(self,widget):
		calendardialog = WindowCalendar(self.data_path,self, date=self.rcd_date.get_text())
		calendardialog.run()

	def setDate(self,date):
		self.rcd_date.set_text(date)

	def setTime(self,timeInSeconds):
		time_in_hour = int(timeInSeconds)/3600.0
		hour = int(time_in_hour)
		min = int((time_in_hour-hour)*60)
		sec = (((time_in_hour-hour)*60)-min)*60
		self.rcd_hour.set_value(hour)
		self.rcd_min.set_value(min)
		self.rcd_second.set_value(sec)

	def setValue(self,var_name,value, format="%0.2f"):
		var = getattr(self,var_name)
		try:
			valueString = format % value
			var.set_text(valueString)
		except Exception as e:
			print var_name, value, e
			pass
	
	def setValues(self,values):
		#(24, u'2009-12-26', 4, 23.48, u'9979', 0.0, 8.4716666232200009, 2210, u'', None, u'', 573.0, 562.0, 11.802745244400001, 5.0499999999999998, 7.04, 0.0, u'2009-12-25T19:41:48Z', u'2009-12-26 08:41:48+13:00')
		#(50, u'2006-10-13', 1, 25.0, u'5625', 0.0, 16.0, 0, u'', gpsfile, title,upositive,unegative,maxspeed|maxpace|pace|maxbeats
		self.id_record = values[0]
		self.setTime(values[4])
		self.rcd_date.set_text(str(values[1]))
		self.setValue("rcd_distance",values[3])
		self.setValue("rcd_average",values[6])
		self.setValue("rcd_calories",values[7], "%0.0f")
		self.setValue("rcd_beats",values[5], "%0.0f")
		self.setValue("rcd_upositive",values[11])
		self.setValue("rcd_unegative",values[12])
		self.setValue("rcd_maxvel",values[13])
		self.setValue("rcd_maxpace",values[14])
		self.setValue("rcd_pace",values[15])
		self.setValue("rcd_maxbeats",values[16], "%0.0f")
		self.rcd_title.set_text("%s"%values[10])
		
		local_time = values[18]
		if local_time is not None:
			dateTime = dateutil.parser.parse(local_time)
			sTime = dateTime.strftime("%X")
			self.rcd_starttime.set_text("%s" % sTime)
		sportID = values[2]
		sportPosition = self.getSportPosition(sportID)
		self.rcd_sport.set_active(sportPosition) 
		buffer = self.rcd_comments.get_buffer()
		start,end = buffer.get_bounds()
		buffer.set_text(values[8])
		self.mode = "editrecord"

	def getSportPosition(self, sportID):
		"""
			Function to determine the position in the sport array for a given sport ID
			Needed as once sports are deleted there are gaps in the list...
		"""
		count = 0
		for key, value in self.listSport.iteritems():
			if key == sportID: 
				return count
			count +=1
		return 0
		
	def getSportPositionByName(self, sport):
		"""
			Function to determine the position in the sport array for a given sport 
			Needed as once sports are deleted there are gaps in the list...
		"""
		count = 0
		for key, value in self.listSport.iteritems():
			if value == sport: 
				return count
			count +=1
		return None
	
	def on_calctime_clicked(self,widget):
		try:
			distance = self.rcd_distance.get_text()
			average = self.rcd_average.get_text()
			time_in_hour = float(distance)/float(average)
			self.set_recordtime(time_in_hour)
		except:
			pass

	def update_activity_data(self, row, gpx_file, sport):
		self.activity_data[row]["rcd_comments"] = ""
		gpx_summary, laps = self.parent.summaryFromGPX(gpx_file, (sport,""))
		local_time = gpx_summary['date_time_local']
		start_date = local_time.strftime("%Y-%m-%d")
		start_time = local_time.strftime("%H:%M:%S")
		self.activity_data[row]["rcd_date"] = start_date
		self.activity_data[row]["rcd_starttime"] = start_time
		self.activity_data[row]["date_time_local"] = gpx_summary['date_time_local']
		self.activity_data[row]["date_time_utc"] = gpx_summary['date_time_utc']
		self.activity_data[row]["rcd_average"] = gpx_summary["rcd_average"]
		self.activity_data[row]["rcd_calories"] = gpx_summary["rcd_calories"]
		self.activity_data[row]["rcd_beats"] = gpx_summary["rcd_beats"]
		self.activity_data[row]["rcd_upositive"] = gpx_summary["rcd_upositive"]
		self.activity_data[row]["rcd_unegative"] = gpx_summary["rcd_unegative"]
		self.activity_data[row]["rcd_maxvel"] = gpx_summary["rcd_maxvel"]
		self.activity_data[row]["rcd_maxpace"] = gpx_summary["rcd_maxpace"]
		self.activity_data[row]["rcd_pace"] = gpx_summary["rcd_pace"]
		self.activity_data[row]["rcd_maxbeats"] = gpx_summary["rcd_maxbeats"]
		self.activity_data[row]["rcd_title"] = ""
		self.activity_data[row]["laps"] = laps
		self.activity_data[row]["complete"] = True

		
	def show_treeviewEntries_row(self, row):
		'''
		Show details of treeview entry
		TODO need to maintain any changes and display those....
		'''
		self.active_row = row
		#Get details from stored data
		#set sport
		sport = self.activity_data[row]["rcd_sport"]
		sportPosition = self.getSportPositionByName(sport)
		if sportPosition is not None:
			self.rcd_sport.set_active(sportPosition)
		#Set gpx file name
		gpx_file = self.activity_data[row]["rcd_gpxfile"]
		self.setValue("rcd_gpxfile", gpx_file, "%s")
		#set duration
		time = Date().time2second(self.activity_data[row]["rcd_time"])		#TODO Fix to use timeinseconds!!
		self.setTime(time) 													#TODO Fix to use timeinseconds!!
		#Set distance
		self.setValue("rcd_distance",self.activity_data[row]["rcd_distance"], "%s")
		#Set comments
		buffer = self.rcd_comments.get_buffer()
		start,end = buffer.get_bounds()
		if "rcd_comments" not in self.activity_data[row]:
			self.activity_data[row]["rcd_comments"] = ""
		buffer.set_text(self.activity_data[row]["rcd_comments"])
		while gtk.events_pending():	# This allows the GUI to update 
			gtk.main_iteration()	# before completion of this entire action
		if self.activity_data[row]["complete"] is False:
			#Haven't processed GPX file yet
			#Blank values not yet known
			self.setValue("rcd_date", "", "%s")
			self.setValue("rcd_starttime", "", "%s")
			self.setValue("rcd_average", "", "%s")
			self.setValue("rcd_calories","", "%s")
			self.setValue("rcd_beats", "", "%s")
			self.setValue("rcd_upositive", "", "%s")
			self.setValue("rcd_unegative", "", "%s")
			self.setValue("rcd_maxvel", "", "%s")
			self.rcd_maxpace.set_text("")
			self.rcd_pace.set_text("")
			self.setValue("rcd_maxbeats", "", "%s")
			while gtk.events_pending():	# This allows the GUI to update 
				gtk.main_iteration()	# before completion of this entire action
			#Get some info from gpx file
			self.update_activity_data(row, gpx_file, sport)
			
		self.setValue("rcd_date", self.activity_data[row]["rcd_date"], "%s")
		self.setValue("rcd_starttime", self.activity_data[row]["rcd_starttime"], "%s")
		self.setValue("rcd_average",self.activity_data[row]["rcd_average"])
		self.setValue("rcd_calories",self.activity_data[row]["rcd_calories"], "%s")
		self.setValue("rcd_beats",self.activity_data[row]["rcd_beats"], "%s")
		self.setValue("rcd_upositive",self.activity_data[row]["rcd_upositive"], "%s")
		self.setValue("rcd_unegative",self.activity_data[row]["rcd_unegative"], "%s")
		self.setValue("rcd_maxvel",self.activity_data[row]["rcd_maxvel"])
		self.rcd_maxpace.set_text(self.activity_data[row]["rcd_maxpace"])
		self.rcd_pace.set_text(self.activity_data[row]["rcd_pace"])
		self.setValue("rcd_maxbeats",self.activity_data[row]["rcd_maxbeats"], "%s")
		self.rcd_title.set_text(self.activity_data[row]["rcd_title"])
		
		
	def on_rcd_title_changed(self, widget):
		if self.mode == "multiple_activities" and self.active_row is not None:
			self.activity_data[self.active_row]["rcd_title"] = self.rcd_title.get_text()
			
	def on_rcd_sport_changed(self, widget):
		if self.mode == "multiple_activities" and self.active_row is not None:
			sport = self.rcd_sport.get_active_text()
			#Update sport in data store
			self.activity_data[self.active_row]["rcd_sport"] = sport
			#Update sport in treeview
			self.store[self.active_row][4] = sport
			
	def on_rcd_distance_changed(self, widget):
		if self.mode == "multiple_activities" and self.active_row is not None:
			distance = self.rcd_distance.get_text()
			#Update distance in data store
			self.activity_data[self.active_row]["rcd_distance"] = distance
			#Update distance in treeview
			self.store[self.active_row][2] = distance
			
	def on_rcd_duration_value_changed(self, widget):
		if self.mode == "multiple_activities" and self.active_row is not None:
			hour = self.rcd_hour.get_value()
			min = self.rcd_min.get_value()
			sec = self.rcd_second.get_value()
			#print hour, min, sec
			#Update duration in data store
			self.activity_data[self.active_row]["rcd_time"] = (hour, min, sec)
			#Update duration in treeview
			self.store[self.active_row][3] = "%d:%.2d:%.2d" % (int(hour), int(min), int(sec))
			
	def on_rcd_date_changed(self, widget):
		if self.mode == "multiple_activities" and self.active_row is not None:
			#Update date in data store
			self.activity_data[self.active_row]["rcd_date"] = self.rcd_date.get_text()
			
	def on_rcd_starttime_changed(self, widget):
		if self.mode == "multiple_activities" and self.active_row is not None:
			#Update start time in data store
			self.activity_data[self.active_row]["rcd_starttime"] = self.rcd_starttime.get_text()
			
	def on_treeviewEntries_row_activated(self, treeview, event):
		'''
		 Callback to display details of different activity
		'''
		#Check for edited data in previous row
		if self.active_row is not None:
			#Check for edited data in comments
			buffer = self.rcd_comments.get_buffer()
			start,end = buffer.get_bounds()
			comments = buffer.get_text(start,end, True).replace("\"","'")
			self.activity_data[self.active_row]["rcd_comments"] = comments
			#Advanced tab items
			self.activity_data[self.active_row]["rcd_maxpace"] = self.rcd_maxpace.get_text()
			self.activity_data[self.active_row]["rcd_pace"] = self.rcd_pace.get_text()
			self.activity_data[self.active_row]["rcd_upositive"] = self.rcd_upositive.get_text()
			self.activity_data[self.active_row]["rcd_unegative"] = self.rcd_unegative.get_text()
			self.activity_data[self.active_row]["rcd_maxbeats"] = self.rcd_maxbeats.get_text()
			self.activity_data[self.active_row]["rcd_beats"] = self.rcd_beats.get_text()
			self.activity_data[self.active_row]["rcd_calories"] = self.rcd_calories.get_text()
		#Get row that was selected
		x = int(event.x)
		y = int(event.y)
		time = event.time
		pthinfo = treeview.get_path_at_pos(x, y)
		if pthinfo is not None:
			path, col, cellx, celly = pthinfo
			treeview.grab_focus()
			treeview.set_cursor(path, col, 0)
			while gtk.events_pending():	# This allows the GUI to update 
				gtk.main_iteration()	# before completion of this entire action
			self.show_treeviewEntries_row(path[0])
		
	def on_calcaverage_clicked(self,widget):
		try:
			hour = self.rcd_hour.get_value_as_int()
			min = self.rcd_min.get_value_as_int()
			sec = self.rcd_second.get_value_as_int()
			time = sec + (min*60) + (hour*3600)
			time_in_hour = time/3600.0
			distance = float(self.rcd_distance.get_text())
			average = distance/time_in_hour
			self.rcd_average.set_text("%0.2f" %average)
		except:
			pass
	
	def on_calcpace_clicked(self,widget):
		hour = self.rcd_hour.get_value_as_int()
		min = self.rcd_min.get_value_as_int()
		sec = self.rcd_second.get_value_as_int()
		time = sec + (min*60) + (hour*3600)
		if time<1:
			return False
		time_in_min = time/60.0
		distance = float(self.rcd_distance.get_text())
		if distance<1:
			return False
		average = time_in_min/distance
		self.rcd_pace.set_text("%0.2f" %average)
	
	def on_calccalories_clicked(self,widget):
		sport = self.rcd_sport.get_active_text()
		hour = self.rcd_hour.get_value_as_int()
		min = self.rcd_min.get_value_as_int()
		sec = self.rcd_second.get_value_as_int()
		hour += min/60 + sec/60/60
		weight = float("0%s"%self.parent.configuration.getValue("pytraining","prf_weight"))
		met = self.parent.getSportMet(sport)
		extraweight = self.parent.getSportWeight(sport)
		if met:
			calories = met*(weight+extraweight)*hour
			self.rcd_calories.set_text(str(calories))

	def on_calcdistance_clicked(self,widget):
		try:
			hour = self.rcd_hour.get_value_as_int()
			min = self.rcd_min.get_value_as_int()
			sec = self.rcd_second.get_value_as_int()
			time = sec + (min*60) + (hour*3600)
			time_in_hour = time/3600.0
			average = float(self.rcd_average.get_text())
			distance = average*time_in_hour
			self.set_distance(distance) 
		except:
			pass
	
	def set_distance(self,distance):
		self.rcd_distance.set_text("%0.2f" %distance)
			
	def set_maxspeed(self,vel):
		self.rcd_maxvel.set_text("%0.2f" %vel)
			
	def set_maxhr(self,hr):
		self.rcd_maxbeats.set_text("%0.2f" %hr)
			
	def set_recordtime (self,time_in_hour):
		hour = int(time_in_hour)
		min = int((time_in_hour-hour)*60)
		sec = (((time_in_hour-hour)*60)-min)*60
		self.rcd_hour.set_value(hour)
		self.rcd_min.set_value(min)
		self.rcd_second.set_value(sec)

	def on_selectfile_clicked(self,widget):
		self.filechooser = FileChooser(self.data_path,self,"set_gpxfile","open")
		self.filechooser.run()

	def set_gpxfile(self):
		namefile = self.filechooser.filename
		self.rcd_gpxfile.set_text(namefile)

	def on_calculatevalues_clicked(self,widget):
		gpxfile = self.rcd_gpxfile.get_text()
		if os.path.isfile(gpxfile):
			self.frameGeneral.set_sensitive(0)
			self.frameVelocity.set_sensitive(0)	
			self.parent.actualize_fromgpx(gpxfile)

