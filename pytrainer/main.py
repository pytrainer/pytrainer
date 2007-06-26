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

import locale
import sys
import os
import pygtk
import gobject
pygtk.require('2.0')
import gtk
import gtk.glade

from record import Record
from extension import Extension
from plugins import Plugins
from profile import Profile
from recordgraph import RecordGraph
from daygraph import DayGraph
from monthgraph import MonthGraph
from yeargraph import YearGraph

from extensions.googlemaps import Googlemaps
from extensions.waypointeditor import WaypointEditor

#from gui.windowextensions import WindowExtensions
from gui.windowmain import Main
from gui.warning import Warning
from lib.system import checkConf
from lib.date import Date
from lib.gpx import Gpx
from lib.soapUtils import webService

class pyTrainer:
	def __init__(self,filename = None, data_path = None):
		self.data_path = data_path
		#configuration
		self.version ="1.4.2"
		self.conf = checkConf()
		#Lanzamos el webservice para las extensiones
		self.webservice = webService(self.conf)
		self.webservice.start()
		#self.webservice.run()
		#preparamos la ventana principal
		self.windowmain = Main(data_path,self,self.version)
		self.date = Date(self.windowmain.calendar)

		#comprobamos que el profile esta configurado
		self.profile = Profile(self.data_path,self)
		self.profile.setVersion(self.version)
		if self.profile.isProfileConfigured():
			self.windowmain.window_sensitive(1)
		#if self.profile.isProfileConfigured():
		#	self.windowmain.window_sensitive(1)
		#else:
		#	self.windowmain.window_sensitive(0)

		self.record = Record(data_path,self,self.version)
		self.extension = Extension(data_path)
		self.plugins = Plugins(data_path)
		self.loadPlugins()
		self.loadExtensions()
		self.windowmain.createGraphs(RecordGraph,DayGraph,MonthGraph,YearGraph)
		self.windowmain.createMap(Googlemaps)
		self.windowmain.createWaypointEditor(WaypointEditor)
		self.windowmain.on_calendar_selected(None)
	
		self.refreshMainSportList()	
		self.windowmain.run()

	def loadPlugins(self):	
		activeplugins = self.plugins.getActivePlugins()
		if (len(activeplugins)<1):
			print _("No Active Plugins")
		else:
			for plugin in activeplugins:
				txtbutton = self.plugins.loadPlugin(plugin)
				self.windowmain.addImportPlugin(txtbutton)
	
	def loadExtensions(self):	
		activeextensions = self.extension.getActiveExtensions()
		if (len(activeextensions)<1):
			print _("No Active Extensions")
		else:
			for extension in activeextensions:
				txtbutton = self.extension.loadExtension(extension)
				self.windowmain.addExtension(txtbutton)
	
	def runPlugin(self,widget,pathPlugin):
		gpxfile = self.plugins.runPlugin(pathPlugin)
		list_sport = self.profile.getSportList()
		self.record.newGpxRecord(gpxfile,list_sport)
	
	def runExtension(self,extension,id):
		txtbutton,pathExtension,type = extension
		if type == "record":
			#Si es record le tenemos que crear el googlemaps, el gpx y darle el id de la bbdd
			alert = self.extension.runExtension(pathExtension,id)
	
	def refreshMainSportList(self):
		listSport = self.profile.getSportList()
		self.windowmain.updateSportList(listSport)
		
	def refreshGraphView(self, view, sport=None):
		date_selected = self.date.getDate()
		if view=="record":
			selected,iter = self.windowmain.recordTreeView.get_selection().get_selected()
			if iter:
				id_record = selected.get_value(iter,0)
				record_list = self.record.getrecordInfo(id_record)
				gpxfile = self.conf.getValue("gpxdir")+"/%s.gpx" %id_record
				if os.path.isfile(gpxfile):
					gpx = Gpx(self.data_path,gpxfile)
					gpx_tracklist = gpx.getTrackList()
					self.refreshMapView()
				else: gpx_tracklist = []
			else:
				record_list=[]
				gpx_tracklist = []
			self.windowmain.actualize_recordview(record_list)
			self.windowmain.actualize_recordgraph(gpx_tracklist)
			 
		elif view=="day":
			record_list = self.record.getrecordList(date_selected)
			self.windowmain.actualize_dayview(record_list)
			selected,iter = self.windowmain.recordTreeView.get_selection().get_selected()
				
		elif view=="month":
			date_ini, date_end = self.date.getMonthInterval(date_selected)
			sport = self.windowmain.getSportSelected()
                	record_list = self.record.getrecordPeriodSport(date_ini, date_end,sport)
			nameMonth = self.date.getNameMonth(date_selected)
			self.windowmain.actualize_monthview(record_list, nameMonth)
			self.windowmain.actualize_monthgraph(record_list)
		elif view=="year":
			date_ini, date_end = self.date.getYearInterval(date_selected)
			sport = self.windowmain.getSportSelected()
			year = self.date.getYear(date_selected)
                	record_list = self.record.getrecordPeriodSport(date_ini, date_end,sport)
			self.windowmain.actualize_yearview(record_list, year)
			self.windowmain.actualize_yeargraph(record_list)
			
	def refreshMapView(self):
		selected,iter = self.windowmain.recordTreeView.get_selection().get_selected()
		id_record = selected.get_value(iter,0)
		self.windowmain.actualize_map(id_record)

	def refreshListRecords(self):
		date = self.date.getDate()
		record_list = self.record.getrecordList(date)
		self.windowmain.actualize_recordTreeView(record_list)
		record_list = self.record.getRecordDayList(date)
		self.windowmain.actualize_calendar(record_list)

	def refreshListView(self):
		record_list = self.record.getAllRecordList()
		self.windowmain.actualize_listview(record_list)
	
	def searchListView(self,condition):
		record_list = self.record.getRecordListByCondition(condition)
		self.windowmain.actualize_listview(record_list)
		
	def editExtensions(self):
                self.extension.manageExtensions()
		
	def editGpsPlugins(self):
		self.plugins.managePlugins()

	def newRecord(self):
		list_sport = self.profile.getSportList()
		date = self.date.getDate()
                self.record.newRecord(list_sport, date)

	def editRecord(self, id_record):
		list_sport = self.profile.getSportList()
                self.record.editRecord(id_record,list_sport)

	def removeRecord(self, id_record, confirm = False):
		if confirm:
			self.record.removeRecord(id_record)
		else:
			msg = _("You are going to remove one database entry. Are you sure yo want do it?")
			params = [id_record,True]
			warning = Warning(self.data_path,self.removeRecord,params)
			warning.set_text(msg)
			warning.run()
	
	def exportCsv(self):
		from save import Save
		save = Save(self.data_path, self.record)
		save.run()		
	
	def editProfile(self):
		self.profile.editProfile()
