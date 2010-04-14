#Copyright (C) Fiz Vazquez vud1@sindominio.net
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

import gobject
import sys
import logging
import datetime
import matplotlib

import dateutil.parser
from dateutil.tz import * # for tzutc()

from SimpleGladeApp import *
from popupmenu import PopupMenu
from aboutdialog import About

from pytrainer.lib.date import Date
#from pytrainer.lib.system import checkConf
from pytrainer.lib.xmlUtils import XMLParser
from pytrainer.lib.gpx import Gpx
from pytrainer.lib.unitsconversor import *

class Main(SimpleGladeApp):
	def __init__(self, data_path = None, parent = None, version = None, gpxDir = None):
		def url_hook(dialog, url):
			pytrainer.lib.webUtils.open_url_in_browser(url)
		# Available in PyGTK 2.6 and above
		gtk.about_dialog_set_url_hook(url_hook)
		self.version = version
		self.parent = parent
		self.pytrainer_main = parent
		self.data_path = data_path
		glade_path="glade/pytrainer.glade"
		root = "window1"
		domain = None
		SimpleGladeApp.__init__(self, self.data_path+glade_path, root, domain)

		self.popup = PopupMenu(data_path,self)
		self.block = False
		self.activeSport = None
		self.gpxDir = gpxDir
		self.record_list = None
		self.laps = None
		self.y1_limits = None
		self.y1_color = None
		self.y1_linewidth = 1

	def new(self):
		self.testimport = self.pytrainer_main.startup_options.testimport
		self.menublocking = 0
		self.selected_view="day"
		self.window1.set_title ("pyTrainer %s" % self.version)
		self.record_list = []
		#create the columns for the listdayrecord
		column_names=[_("id"),_("Start"), _("Sport"),_("Kilometer")]
		self.create_treeview(self.recordTreeView,column_names)
		#create the columns for the listarea
		column_names=[_("id"),_("Title"),_("Date"),_("Distance"),_("Sport"),_("Time"),_("Beats"),_("Average"),("Calories")]
		self.create_treeview(self.allRecordTreeView,column_names)
		self.create_menulist(column_names)
		#create the columns for the waypoints treeview
		column_names=[_("id"),_("Waypoint")]
		self.create_treeview(self.waypointTreeView,column_names)
		#conf = checkConf()
		self.fileconf = self.pytrainer_main.profile.confdir+"/listviewmenu.xml"
		if not os.path.isfile(self.fileconf):
			self._createXmlListView(self.fileconf)
		self.showAllRecordTreeViewColumns()
		self.allRecordTreeView.set_search_column(1)
		self.notebook.set_current_page(1)

		#Disable import menu item unless specified on startup
		self.set_unified_import(self.testimport)
			
	def set_unified_import(self, status=False):
		self.menu_importdata.set_sensitive(status)
		self.parent.testimport = status
			
	def _createXmlListView(self,file):
		menufile = XMLParser(file)
		savedOptions = []
		savedOptions.append(("date","True"))
		savedOptions.append(("distance","True"))
		savedOptions.append(("average","False"))
		savedOptions.append(("title","True"))
		savedOptions.append(("sport","True"))
		savedOptions.append(("id_record","False"))
		savedOptions.append(("time","False"))
		savedOptions.append(("beats","False"))
		savedOptions.append(("calories","False"))
		menufile.createXMLFile("listviewmenu",savedOptions)	

	def removeImportPlugin(self, plugin):
		for widget in self.menuitem1_menu:
			if widget.get_name() == plugin[1]:
				self.menuitem1_menu.remove(widget)
				
	def removeExtension(self, extension):
		for widget in self.recordbuttons_hbox:
			if widget.get_name() == extension[1]:
				logging.debug("Removing extension: %s " % extension[0])
				self.recordbuttons_hbox.remove(widget)

	def addImportPlugin(self,plugin):
		button = gtk.MenuItem(plugin[0])
		button.set_name(plugin[1])
		button.connect("activate", self.parent.runPlugin, plugin[1])
		self.menuitem1_menu.insert(button,3)
		self.menuitem1_menu.show_all()

	def addExtension(self,extension):
		#txtbutton,extensioncode,extensiontype = extension
		button = gtk.Button(extension[0])
		button.set_name(extension[1])
		button.connect("button_press_event", self.runExtension, extension)
		self.recordbuttons_hbox.pack_start(button,False,False,0)
		self.recordbuttons_hbox.show_all()

	def runExtension(self,widget,widget2,extension):
		#print extension
		txtbutton,extensioncode,extensiontype = extension
		id = None
		if extensiontype=="record":
			selected,iter = self.recordTreeView.get_selection().get_selected()
			id = selected.get_value(iter,0)
		self.parent.runExtension(extension,id)

	def createGraphs(self,RecordGraph,DayGraph,WeekGraph, MonthGraph,YearGraph,HeartRateGraph):
		self.drawarearecord = RecordGraph(self.record_graph_vbox, self.window1, self.record_combovalue, self.record_combovalue2, self.btnShowLaps, self.tableConfig)
		self.drawareaheartrate = HeartRateGraph(self.heartrate_vbox, self.window1, self.heartrate_vbox2)
		#self.drawareaday = DayGraph(self.day_vbox, self.day_combovalue)
		self.day_vbox.hide()
		self.drawareaweek = WeekGraph(self.weekview, self.window1, self.week_combovalue, self.week_combovalue2)
		self.drawareamonth = MonthGraph(self.month_vbox, self.window1, self.month_combovalue,self.month_combovalue2)
		self.drawareayear = YearGraph(self.year_vbox, self.window1, self.year_combovalue,self.year_combovalue2)
	
	def createMap(self,Googlemaps,waypoint):
		self.googlemaps = Googlemaps(self.data_path, self.map_vbox,waypoint, pytrainer_main=self.parent)
		self.googlemaps_old = Googlemaps(self.data_path, self.map_vbox_old,waypoint, pytrainer_main=self.parent)

	def updateSportList(self,listSport): 
		logging.debug(">>")
		liststore =  self.sportlist.get_model()
		if self.sportlist.get_active() is not 0:
			self.sportlist.set_active(0) #Set first item active if it isnt
		firstEntry = self.sportlist.get_active_text()
		liststore.clear() #Delete all items
		#Re-add "All Sports"
		liststore.append([firstEntry])
		#Re-add all sports in listSport
		for i in listSport:
			liststore.append([i[0]])
		self.sportlist.set_active(0)
		logging.debug("<<")

	def create_treeview(self,treeview,column_names):
		i=0
		for column_index, column_name in enumerate(column_names):
			column = gtk.TreeViewColumn(column_name, gtk.CellRendererText(), text=column_index)
			column.set_resizable(True)
			if i==0:
				column.set_visible(False)
			column.set_sort_column_id(i)
			treeview.append_column(column)
			i+=1
	
	def actualize_recordview(self,record_list):
		logging.debug(">>")
		if self.pytrainer_main.profile.getValue("pytraining","prf_us_system") == "True":
			self.r_distance_unit.set_text(_("miles"))
			self.r_speed_unit.set_text(_("miles/h"))
			self.r_maxspeed_unit.set_text(_("miles/h"))
			self.r_pace_unit.set_text(_("min/mile"))
			self.r_maxpace_unit.set_text(_("min/mile"))
			self.r_ascent_unit.set_text(_("feet"))
			self.r_descent_unit.set_text(_("feet"))
		else:
			self.r_distance_unit.set_text(_("km"))
			self.r_speed_unit.set_text(_("km/h"))
			self.r_maxspeed_unit.set_text(_("km/h"))
			self.r_pace_unit.set_text(_("min/km"))
			self.r_maxpace_unit.set_text(_("min/km"))
			self.r_ascent_unit.set_text(_("m"))
			self.r_descent_unit.set_text(_("m"))

		if len(record_list)>0:
			record_list=record_list[0]
			
			self.recordview.set_sensitive(1)
			sport = record_list[0]
			date = record_list[1]
			distance = self.parseFloat(record_list[2])
			average = self.parseFloat(record_list[6])
			calories = self.parseFloat(record_list[7])
			upositive = self.parseFloat(record_list[10])
			unegative = self.parseFloat(record_list[11])
			title = str(record_list[9])
			comments = str(record_list[5])
			pace = self.parseFloat(record_list[14]) #to review
			maxspeed = self.parseFloat(record_list[12]) #to review
			maxpace = self.parseFloat(record_list[13])

			#Get datetime from DB, use local time if available otherwise use date_time_utc and create a local datetime...
			#TODO get data from date_time_local and parse 
			date_time_local = record_list[17]
			date_time_utc = record_list[16]
			if date_time_local is not None: #Have a local time stored in DB
				dateTime = dateutil.parser.parse(date_time_local)
			else: #No local time in DB
				tmpDateTime = dateutil.parser.parse(date_time_utc)
				dateTime = tmpDateTime.astimezone(tzlocal()) #datetime with localtime offset (using value from OS)
			recordDateTime = dateTime.strftime("%Y-%m-%d %H:%M:%S")
			recordDate = dateTime.strftime("%x")
			recordTime = dateTime.strftime("%X")
			recordDateTimeOffset = dateTime.strftime("%z")
			
			if self.pytrainer_main.profile.getValue("pytraining","prf_us_system") == "True":
				self.record_distance.set_text("%0.2f" %km2miles(distance))
				self.record_upositive.set_text("%0.2f" %m2feet(upositive))
				self.record_unegative.set_text("%0.2f" %m2feet(unegative))
				self.record_average.set_text("%0.2f" %km2miles(average))
				self.record_maxspeed.set_text("%0.2f" %km2miles(maxspeed))
				self.record_pace.set_text("%0.2f" %pacekm2miles(pace))
				self.record_maxpace.set_text("%0.2f" %pacekm2miles(maxpace))
		
			else:
				self.record_distance.set_text("%0.2f" %distance)
				self.record_upositive.set_text("%0.2f" %upositive)
				self.record_unegative.set_text("%0.2f" %unegative)
				self.record_average.set_text("%0.2f" %average)
				self.record_maxspeed.set_text("%0.2f" %maxspeed)
				self.record_pace.set_text("%0.2f" %pace)
				self.record_maxpace.set_text("%0.2f" %maxpace)
			
			self.record_sport.set_text(sport)
			#self.record_date.set_text(str(date))
			self.record_date.set_text(recordDate)
			self.record_time.set_text(recordTime)
			hour,min,sec=self.parent.date.second2time(int(record_list[3]))
			self.record_hour.set_text("%d" %hour)
			self.record_minute.set_text("%02d" %min)
			self.record_second.set_text("%02d" %sec)
			self.record_calories.set_text("%0.0f" %calories)
			#self.record_datetime.set_text(recordDateTime)
			#self.record_datetime_offset.set_text(recordDateTimeOffset)
			self.record_title.set_text(title)
			buffer = self.record_comments.get_buffer()
			start,end = buffer.get_bounds()
			buffer.set_text(comments)

		else:
			self.recordview.set_current_page(0)
			self.recordview.set_sensitive(0)
		logging.debug(">>")

	def actualize_recordgraph(self,record_list,laps=None):
		logging.debug(">>")
		self.record_list = record_list
		self.laps = laps
		if len(record_list)>0:
			self.record_vbox.set_sensitive(1)
			self.drawarearecord.drawgraph(record_list,laps)
		else:
			#Remove graph
			vboxChildren = self.record_vbox.get_children()
			logging.debug('Vbox has %d children %s' % (len(vboxChildren), str(vboxChildren) ))
			# ToDo: check why vertical container is shared
			for child in vboxChildren:
				#Remove all FigureCanvasGTK and NavigationToolbar2GTKAgg to stop double ups of graphs
				if isinstance(child, matplotlib.backends.backend_gtkagg.FigureCanvasGTK) or isinstance(child, matplotlib.backends.backend_gtkagg.NavigationToolbar2GTKAgg):
					logging.debug('Removing child: '+str(child))
					self.record_vbox.remove(child)
			self.record_vbox.set_sensitive(0)
		logging.debug("<<")
	
	def actualize_heartrategraph(self,record_list):
		logging.debug(">>")
		self.drawareaheartrate.drawgraph(record_list)
		logging.debug("<<")

	def actualize_hrview(self,record_list,zones,is_karvonen_method):
		logging.debug(">>")
		if len(record_list)>0:
			record_list=record_list[0]
			self.record_zone1.set_text("%s-%s" %(zones[4][0],zones[4][1]))
			self.record_zone2.set_text("%s-%s" %(zones[3][0],zones[3][1]))
			self.record_zone3.set_text("%s-%s" %(zones[2][0],zones[2][1]))
			self.record_zone4.set_text("%s-%s" %(zones[1][0],zones[1][1]))
			self.record_zone5.set_text("%s-%s" %(zones[0][0],zones[0][1]))
			beats = self.parseFloat(record_list[4])
			maxbeats = self.parseFloat(record_list[15])
			self.record_beats.set_text("%0.2f" %beats)
			self.record_maxbeats.set_text("%0.2f" %maxbeats)
			if is_karvonen_method=="True":
				self.record_zonesmethod.set_text(_("Karvonen method"))
			else:
				self.record_zonesmethod.set_text(_("Percentages method"))
		else:
			self.recordview.set_sensitive(0)
		logging.debug("<<")

	def actualize_dayview(self,record_list):
		logging.debug(">>")
		if self.pytrainer_main.profile.getValue("pytraining","prf_us_system") == "True":
			self.d_distance_unit.set_text(_("miles"))
			self.d_speed_unit.set_text(_("miles/h"))
			self.d_maxspeed_unit.set_text(_("miles/h"))
			self.d_pace_unit.set_text(_("min/mile"))
			self.d_maxpace_unit.set_text(_("min/mile"))
		else:
			self.d_distance_unit.set_text(_("km"))
			self.d_speed_unit.set_text(_("km/h"))
			self.d_maxspeed_unit.set_text(_("km/h"))
			self.d_pace_unit.set_text(_("min/km"))
			self.d_maxpace_unit.set_text(_("min/km"))

		if len(record_list)>0:
			tbeats = 0
			distance = 0
			calories = 0
			timeinseconds = 0
			beats = 0
			maxbeats = 0
			maxspeed = 0
			average = 0
			maxpace = "0.00"
			pace = "0.00"
			for record in record_list:
				distance += self.parseFloat(record[2])
				calories += self.parseFloat(record[7])
				timeinseconds += self.parseFloat(record[3])
				beats = self.parseFloat(record[4])
				if float(beats)>0:
					tbeats += beats*(self.parseFloat(record[3])/60/60)
				if record[9] > maxspeed:
					maxspeed = self.parseFloat(record[9])
				if record[10] > maxbeats:
					maxbeats = self.parseFloat(record[10])
			
			if self.pytrainer_main.profile.getValue("pytraining","prf_us_system") == "True":
				distance = km2miles(distance)
				maxspeed = km2miles(maxspeed)
			
			if tbeats > 0:		
				tbeats = tbeats/(timeinseconds/60/60)
			if distance > 0:
				average = distance/(timeinseconds/60/60)
			if maxspeed > 0:
				maxpace = "%d.%02d" %((3600/maxspeed)/60,(3600/maxspeed)%60)
			if average > 0:
				pace = "%d.%02d" %((3600/average)/60,(3600/average)%60)
			
			self.dayview.set_sensitive(1)
			self.day_distance.set_text("%0.2f" %distance)
			hour,min,sec=self.parent.date.second2time(timeinseconds)
			self.day_hour.set_text("%d" %hour)
			self.day_minute.set_text("%02d" %min)
			self.day_second.set_text("%02d" %sec)
			self.day_beats.set_text("%0.2f" %tbeats)
			self.day_maxbeats.set_text("%0.2f" %maxbeats)
			self.day_average.set_text("%0.2f" %average)
			self.day_maxspeed.set_text("%0.2f" %maxspeed)
			self.day_pace.set_text(pace)
			self.day_maxpace.set_text(maxpace)
			self.day_calories.set_text("%0.0f" %calories)
			self.day_topic.set_text(str(record[1]))
			
		else:
			self.dayview.set_sensitive(0)
		logging.debug("<<")
	
	def actualize_daygraph(self,record_list):
		logging.debug(">>")
		if len(record_list)>0:
			self.day_vbox.set_sensitive(1)
		else:
			self.day_vbox.set_sensitive(0)
		self.drawareaday.drawgraph(record_list)
		logging.debug("<<")
	
	def actualize_map(self,id_record, full_screen=False):
		logging.debug(">>")
		if full_screen:
			self.googlemaps_old.drawMap(id_record)
		else:
			self.googlemaps.drawMap(id_record)
		logging.debug("<<")
	
	def actualize_weekview(self, record_list, date_ini, date_end):
		logging.debug(">>")
		date_s = datetime.datetime.strptime(date_ini, "%Y-%m-%d")
		date_e = datetime.datetime.strptime(date_end, "%Y-%m-%d")
		self.week_date.set_text("%s - %s (%d)" % (datetime.datetime.strftime(date_s, "%a %d %b"), datetime.datetime.strftime(date_e, "%a %d %b"), int(datetime.datetime.strftime(date_e, "%W"))+1) )

		km = calories = time = average = beats = 0
		num_records = len(record_list)
		logging.info("Number of records selected week: "+str(num_records))
		time_in_min = 0
		tbeats = 0
		maxspeed = 0
		pace = "0.00"
		maxpace = "0.00"
		maxbeats = 0
		
		if self.pytrainer_main.profile.getValue("pytraining","prf_us_system") == "True":
			self.w_distance_unit.set_text(_("miles"))
			self.w_speed_unit.set_text(_("miles/h"))
			self.w_maxspeed_unit.set_text(_("miles/h"))
			self.w_pace_unit.set_text(_("min/mile"))
			self.w_maxpace_unit.set_text(_("min/mile"))
		else:
			self.w_distance_unit.set_text(_("km"))
			self.w_speed_unit.set_text(_("km/h"))
			self.w_maxspeed_unit.set_text(_("km/h"))
			self.w_pace_unit.set_text(_("min/km"))
			self.w_maxpace_unit.set_text(_("min/km"))

		if num_records>0:
			for record in record_list:
				km += self.parseFloat(record[1])
				time += self.parseFloat(record[2])
				average += self.parseFloat(record[5])
				calories += self.parseFloat(record[6])
				beats = self.parseFloat(record[3])
				if float(beats) > 0:
					time_in_min += time/60
					tbeats += beats*(time/60)
				if record[7] > maxspeed:
					maxspeed = self.parseFloat(record[7])
				if record[8] > maxbeats:
					maxbeats = self.parseFloat(record[8])
			
			if self.pytrainer_main.profile.getValue("pytraining","prf_us_system") == "True":
				km = km2miles(km)
				maxspeed = km2miles(maxspeed)
			
			if time_in_min > 0:
				tbeats = tbeats/time_in_min		
			else:
				tbeats = 0
			average = (km/(time/3600))
		
			if maxspeed > 0:
				#maxpace = 60/maxspeed
				maxpace = "%d.%02d" %((3600/maxspeed)/60,(3600/maxspeed)%60)
			if average > 0:
				#pace = 60/average
				pace = "%d.%02d" %((3600/average)/60,(3600/average)%60)
		
			self.weeka_distance.set_text("%0.2f" %km)
			hour,min,sec = self.parent.date.second2time(time)
			self.weeka_hour.set_text("%d" %hour)
			self.weeka_minute.set_text("%02d" %min)
			self.weeka_second.set_text("%02d" %sec)
			self.weeka_maxbeats.set_text("%0.2f" %(maxbeats))
			self.weeka_beats.set_text("%0.2f" %(tbeats))
			self.weeka_average.set_text("%0.2f" %average)
			self.weeka_maxspeed.set_text("%0.2f" %maxspeed)
			self.weeka_pace.set_text(pace)
			self.weeka_maxpace.set_text(maxpace)
			self.weeka_calories.set_text("%0.0f" %calories)
			self.weekview.set_sensitive(1)
		else:
			self.weekview.set_sensitive(0)
		self.drawareaweek.drawgraph(record_list, date_ini, date_end)
		logging.debug("<<")

	def actualize_monthview(self,record_list, nameMonth):
		logging.debug(">>")
		self.month_date.set_text(nameMonth)
		km = calories = time = average = beats = 0
		num_records = len(record_list)
		time_in_min = 0
		tbeats = 0
		maxspeed = 0
		pace = "0.00"
		maxpace = "0.00"
		maxbeats = 0
		
		if self.pytrainer_main.profile.getValue("pytraining","prf_us_system") == "True":
			self.m_distance_unit.set_text(_("miles"))
			self.m_speed_unit.set_text(_("miles/h"))
			self.m_maxspeed_unit.set_text(_("miles/h"))
			self.m_pace_unit.set_text(_("min/mile"))
			self.m_maxpace_unit.set_text(_("min/mile"))
		else:
			self.m_distance_unit.set_text(_("km"))
			self.m_speed_unit.set_text(_("km/h"))
			self.m_maxspeed_unit.set_text(_("km/h"))
			self.m_pace_unit.set_text(_("min/km"))
			self.m_maxpace_unit.set_text(_("min/km"))
	
		if num_records>0:
			for record in record_list:
				km += self.parseFloat(record[1])
				time += self.parseFloat(record[2])
				average += self.parseFloat(record[5])
				calories += self.parseFloat(record[6])
				beats = self.parseFloat(record[3])
				if float(beats) > 0:
					time_in_min += time/60
					tbeats += beats*(time/60)
				if record[7] > maxspeed:
					maxspeed = self.parseFloat(record[7])
				if record[8] > maxbeats:
					maxbeats = self.parseFloat(record[8])
			
			if self.pytrainer_main.profile.getValue("pytraining","prf_us_system") == "True":
				km = km2miles(km)
				maxspeed = km2miles(maxspeed)
			
			if time_in_min > 0:
				tbeats = tbeats/time_in_min		
			else:
				tbeats = 0
			average = (km/(time/3600))
		
			if maxspeed > 0:
				#maxpace = 60/maxspeed
				maxpace = "%d.%02d" %((3600/maxspeed)/60,(3600/maxspeed)%60)
			if average > 0:
				#pace = 60/average
				pace = "%d.%02d" %((3600/average)/60,(3600/average)%60)
		
			self.montha_distance.set_text("%0.2f" %km)
			hour,min,sec = self.parent.date.second2time(time)
			self.montha_hour.set_text("%d" %hour)
			self.montha_minute.set_text("%02d" %min)
			self.montha_second.set_text("%02d" %sec)
			self.montha_maxbeats.set_text("%0.2f" %(maxbeats))
			self.montha_beats.set_text("%0.2f" %(tbeats))
			self.montha_average.set_text("%0.2f" %average)
			self.montha_maxspeed.set_text("%0.2f" %maxspeed)
			self.montha_pace.set_text(pace)
			self.montha_maxpace.set_text(maxpace)
			self.montha_calories.set_text("%0.0f" %calories)
			self.monthview.set_sensitive(1)
		else:
			self.monthview.set_sensitive(0)
		logging.debug("<<")

	def actualize_monthgraph(self,record_list, daysInMonth):
		logging.debug(">>")
		self.drawareamonth.drawgraph(record_list, daysInMonth)
		logging.debug("<<")
	
	def actualize_yearview(self,record_list, year):
		logging.debug(">>")
		self.year_date.set_text("%d" %int(year))
		km = calories = time = average = beats = 0
		num_records = len(record_list)
		time_in_min = 0
		tbeats = 0
		maxspeed = 0
		pace = "0.00"
		maxpace = "0.00"
		maxbeats = 0
		if num_records>0:
			for record in record_list:
				km += self.parseFloat(record[1])
				time += self.parseFloat(record[2])
				average += self.parseFloat(record[5])
				calories += self.parseFloat(record[6])
				beats = self.parseFloat(record[3])
				if float(beats) > 0:
					time_in_min += time/60
					tbeats += beats*(time/60)
				if record[7] > maxspeed:
					maxspeed = self.parseFloat(record[7])
				if record[8] > maxbeats:
					maxbeats = self.parseFloat(record[8])
			if time_in_min > 0:
				tbeats = tbeats/time_in_min		
			else:
				tbeats = 0
			average = (km/(time/3600))
			
			if maxspeed > 0:
				#maxpace = 60/maxspeed
				maxpace = "%d.%02d" %((3600/maxspeed)/60,(3600/maxspeed)%60)
			if average > 0:
				#pace = 60/average
				pace = "%d.%02d" %((3600/average)/60,(3600/average)%60)

			self.yeara_distance.set_text("%0.2f" %km)
			hour,min,sec = self.parent.date.second2time(time)
			self.yeara_hour.set_text("%d" %hour)
			self.yeara_minute.set_text("%02d" %min)
			self.yeara_second.set_text("%02d" %sec)
			self.yeara_beats.set_text("%0.2f" %tbeats)
			self.yeara_maxbeats.set_text("%0.2f" %(maxbeats))
			self.yeara_average.set_text("%0.2f" %average)
			self.yeara_maxspeed.set_text("%0.2f" %maxspeed)
			self.yeara_pace.set_text(pace)
			self.yeara_maxpace.set_text(maxpace)
			self.yeara_calories.set_text("%0.0f" %calories)
			self.yearview.set_sensitive(1)
		else:
			self.yearview.set_sensitive(0)
			self.drawareayear.drawgraph([])
		logging.debug("<<")
	
	def actualize_yeargraph(self,record_list):
		logging.debug(">>")
		self.drawareayear.drawgraph(record_list)
		logging.debug("<<")

	def actualize_listview(self,record_list):
		logging.debug(">>")
		#recod list tiene:
		#date,distance,average,title,sports.name,id_record,time,beats,caloriesi
		#Laas columnas son:
		#column_names=[_("id"),_("Title"),_("Date"),_("Distance"),_("Sport"),_("Time"),_("Beats"),_("Average"),("Calories")]

		date = Date()
		store = gtk.ListStore(
			gobject.TYPE_INT,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_FLOAT,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			object)
		for i in record_list:
			hour,min,sec = date.second2time(int(i[6]))
			time = "%d:%d:%d" %(hour,min,sec)
			iter = store.append()
			store.set (
				iter,
				0, int(i[5]),
				1, str(i[3]),
				2, str(i[0]),
				3, float(i[1]),
				4, str(i[4]),
				5, time,
				6, str(i[7]),
				7, str(i[2]),
				8, str(i[8])
				)
		#self.allRecordTreeView.set_headers_clickable(True)
		self.allRecordTreeView.set_model(store)
		logging.debug("<<")

	def actualize_waypointview(self,record_list,default_waypoint,redrawmap = 1):
		logging.debug(">>")
		#redrawmap: indica si tenemos que refrescar tb el mapa. 1 si 0 no
		#waypoint list tiene:
		#id_waypoint,lat,lon,ele,comment,time,name,sym
		#Laas columnas son:
		#column_names=[_("id"),_("Waypoint")]

		store = gtk.ListStore(
			gobject.TYPE_INT,
			gobject.TYPE_STRING,
			object)
		iterOne = False
		iterDefault = False
		counter = 0
		default_id = 0
		for i in record_list:
			iter = store.append()
			if not iterOne:
				iterOne = iter
			if int(i[0])==default_waypoint:
				iterDefault = iter
				default_id = counter
			store.set (
				iter,
				0, int(i[0]),
				1, str(i[6])
				)
			counter+=1

		self.waypointTreeView.set_model(store)
		if iterDefault:
			self.waypointTreeView.get_selection().select_iter(iterDefault)
		elif iterOne:
			self.waypointTreeView.get_selection().select_iter(iterOne)
		if len(record_list) > 0:
			self.waypoint_latitude.set_text(str(record_list[default_id][1]))
			self.waypoint_longitude.set_text(str(record_list[default_id][2]))
			self.waypoint_name.set_text(str(record_list[default_id][6]))
			self.waypoint_description.set_text(str(record_list[default_id][4]))
			self.set_waypoint_type(str(record_list[default_id][7]))
		if redrawmap == 1:
			self.waypointeditor.createHtml(default_waypoint)
			self.waypointeditor.drawMap()
		logging.debug("<<")
	
	def set_waypoint_type(self, type):
		x = 0
		tree_model = self.waypoint_type.get_model()
		if tree_model is not None:
			#iter = tree_model.get_iter_root()
			for item in tree_model:
				#if isinstance(item, gtk.TreeModelRow):
				if item[0] == type:
					self.waypoint_type.set_active(x)
					return
				x += 1
		self.waypoint_type.insert_text(0, type)
		self.waypoint_type.set_active(0)
		return
			
	
	def on_waypointTreeView_button_press(self, treeview, event):
		x = int(event.x)
		y = int(event.y)
		time = event.time
		pthinfo = treeview.get_path_at_pos(x, y)
		if pthinfo is not None:
			path, col, cellx, celly = pthinfo
			treeview.grab_focus()
			treeview.set_cursor(path, col, 0)
			if event.button == 1:
    				selected,iter = treeview.get_selection().get_selected()
				id_waypoint=selected.get_value(iter,0)
				self.parent.refreshWaypointView(id_waypoint)
		return False
	
	def on_listareasearch_clicked(self,widget):
		lisOpt = {
			_("Title"):"title",
			_("Date"):"date",
			_("Distance"):"distance",
			_("Sport"):"sport",
			_("Time"):"time",
			_("Beats"):"beats",
			_("Average"):"average",
			_("Calories"):"calories" 
			}
		search_string = self.lsa_searchvalue.get_text()
		#ddbb_field = lisOpt[self.lsa_searchoption.get_active_text()]
		self.parent.searchListView("title like '%"+search_string+"%'")	
	
	def create_menulist(self,column_names):
		i=0
		for name in column_names:
			if i!=0:
				item = gtk.CheckMenuItem(name)
				#self.lsa_searchoption.append_text(name)
				item.connect("button_press_event", self.on_menulistview_activate, i)
				self.menulistviewOptions.append(item)
			i+=1
		self.menulistviewOptions.show_all()
	
	def on_menulistview_activate(self,widget,widget2,widget_position):
		listMenus = {
			0:"title",
			1:"date",
			2:"distance",
			3:"sport",
			4:"time",
			5:"beats",
			6:"average",
			7:"calories" }
		
		items = self.menulistviewOptions.get_children()
		if items[widget_position-1].get_active():
			newValue = "False"
		else:
			newValue = "True"
		menufile = XMLParser(self.fileconf)
		menufile.setValue("listviewmenu",listMenus[widget_position-1],newValue)
		self.showAllRecordTreeViewColumns()
	
	def showAllRecordTreeViewColumns(self):
		menufile = XMLParser(self.fileconf)
		listMenus = {
			"id_record":0,
			"title":1,
			"date":2,
			"distance":3,
			"sport":4,
			"time":5,
			"beats":6,
			"average":7,
			"calories":8 }
		columns = self.allRecordTreeView.get_columns()
		menuItems = self.menulistviewOptions.get_children()
		for column in listMenus:
			visible = menufile.getValue("listviewmenu",column)
			if visible == "True":
				visible = True
			else:
				visible = False
			numcolumn = listMenus[column]
			#show the selected columns
			columns[numcolumn].set_visible(visible)
			#select the choice in the menu
			if numcolumn != 0 and self.menublocking != 1:
				menuItems[numcolumn-1].set_active(visible)
		self.menublocking = 1
	
	def createWaypointEditor(self,WaypointEditor,waypoint, parent=None):
		self.waypointeditor = WaypointEditor(self.data_path, self.waypointvbox,waypoint,parent)
		
	def zoom_graph(self, y1limits=None, y1color=None, y1_linewidth=1):
		logging.debug(">>")
		logging.debug("Reseting graph Y axis with ylimits: %s" % str(y1limits) )
		self.drawarearecord.drawgraph(self.record_list,self.laps, y1limits=y1limits, y1color=y1color, y1_linewidth=y1_linewidth)
		logging.debug("<<")

	######################
	## Lista de eventos ##
	######################
	
	def on_spinbuttonY1_value_changed(self, widget):
		y1min = self.spinbuttonY1Min.get_value()
		y1max = self.spinbuttonY1Max.get_value()
		#Check to see if the min and max have the same...
		if y1min == y1max: 
			if widget.get_name() == "spinbuttonY1Min": #User was changing the min spinbutton, so move max up
				y1max += 1
			else:	#Move min down
				y1min -= 1
		self.y1_limits=(y1min, y1max)
		self.zoom_graph(y1limits=self.y1_limits, y1color=self.y1_color, y1_linewidth=self.y1_linewidth)
	
	def on_buttonResetGraph_clicked(self, widget):
		#self.zoom_graph()
		#Reset stored values
		self.y1_limits = None
		self.y1_color = None
		self.y1_linewidth = 1
		self.zoom_graph()
		
	def on_colorbuttonY1LineColor_color_set(self, widget):
		y1color = widget.get_color()
		cs = y1color.to_string()
		self.y1_color = cs[0:3] + cs[5:7] + cs[9:11]
		self.drawarearecord.drawgraph(self.record_list,self.laps, y1limits=self.y1_limits, y1color=self.y1_color, y1_linewidth=self.y1_linewidth)
		
	def on_spinbuttonY1LineWeight_value_changed(self, widget):
		self.y1_linewidth = self.spinbuttonY1LineWeight.get_value_as_int()
		self.drawarearecord.drawgraph(self.record_list,self.laps, y1limits=self.y1_limits, y1color=self.y1_color, y1_linewidth=self.y1_linewidth)

	def on_edit_clicked(self,widget):
		selected,iter = self.recordTreeView.get_selection().get_selected()
		id_record = selected.get_value(iter,0)
		self.parent.editRecord(id_record)

	def on_remove_clicked(self,widget):
		selected,iter = self.recordTreeView.get_selection().get_selected()
		id_record = selected.get_value(iter,0)
		self.parent.removeRecord(id_record)
	
	def on_export_csv_activate(self,widget):
		self.parent.exportCsv()
	
	def on_newrecord_clicked(self,widget):
		self.parent.newRecord()
	
	def on_edituser_activate(self,widget):
		self.parent.editProfile()
	
	def on_calendar_doubleclick(self,widget):
		self.parent.newRecord()
	
	def on_sportlist_changed(self,widget):
		logging.debug("--")
		if self.sportlist.get_active() != self.activeSport:
			self.activeSport = self.sportlist.get_active()
			self.parent.refreshGraphView(self.selected_view)
		else:
			logging.debug("on_sportlist_changed called with no change")
	
	def on_page_change(self,widget,gpointer,page):
		logging.debug("--")
		if page == 0:
			self.selected_view="record"
		elif page == 1:
			self.selected_view="day"
		elif page == 2:
			self.selected_view="week"
		elif page == 3:
			self.selected_view="month"
		elif page == 4:
			self.selected_view="year"
		self.parent.refreshGraphView(self.selected_view)
	
	def on_recordpage_change(self,widget,gpointer,page):
		if page == 0:
			selected_view="info"
		elif page == 1:
			selected_view="graphs"
		elif page == 2:
			selected_view="map"
		elif page == 3:
			selected_view="heartrate"
		self.parent.refreshRecordGraphView(selected_view)
	
	def on_showmap_clicked(self,widget):
		self.infoarea.hide()
		self.maparea.show()
		self.parent.refreshMapView(full_screen=True)
	
	def on_hidemap_clicked(self,widget):
		self.maparea.hide()
		self.infoarea.show()

	def on_btnShowLaps_toggled(self,widget):
		logging.debug("--")
		self.parent.refreshGraphView(self.selected_view)
	
	def on_day_combovalue_changed(self,widget):
		logging.debug("--")
		self.parent.refreshGraphView(self.selected_view)
	
	def on_week_combovalue_changed(self,widget):
		logging.debug("--")
		self.parent.refreshGraphView(self.selected_view)

	def on_month_combovalue_changed(self,widget):
		logging.debug("--")
		self.parent.refreshGraphView(self.selected_view)
	
	def on_year_combovalue_changed(self,widget):
		logging.debug("--")
		self.parent.refreshGraphView(self.selected_view)
	
	def on_calendar_selected(self,widget):
		logging.debug("--")
		if self.block:
			self.block = False
		else:
			if self.selected_view == "record":
				self.recordview.set_current_page(0)
				self.parent.refreshRecordGraphView("info")
			self.parent.refreshListRecords()
			self.parent.refreshGraphView(self.selected_view)

	def on_calendar_changemonth(self,widget):
		logging.debug("--")
		self.block = True
		self.notebook.set_current_page(3)
		self.selected_view="month"
		self.parent.refreshListRecords()
		self.parent.refreshGraphView(self.selected_view)
	
	def on_calendar_next_year(self,widget):
		logging.debug("--")
		self.block = True
		self.notebook.set_current_page(4)
		self.selected_view="year"
		self.parent.refreshListRecords()
		self.parent.refreshGraphView(self.selected_view)
	
	def on_classicview_activate(self,widget):
		self.waypointarea.hide()
		self.listarea.hide()
		self.classicarea.show()
	
	def on_listview_activate(self,widget):
		self.waypointarea.hide()
		self.classicarea.hide()
		self.parent.refreshListView()
		self.listarea.show()
	
	def on_waypointsview_activate(self,widget):
		self.listarea.hide()
		self.classicarea.hide()
		self.parent.refreshWaypointView()
		self.waypointarea.show()

	def on_menu_importdata_activate(self,widget):
		self.parent.importData()
	
	def on_extensions_activate(self,widget):
		self.parent.editExtensions()

	def on_gpsplugins_activate(self,widget):
		self.parent.editGpsPlugins()
	#hasta aqui revisado
	
	def on_allRecordTreeView_button_press(self, treeview, event):
		logging.debug(">>")
		#print "on_allRecordTreeView_"
		x = int(event.x)
		y = int(event.y)
		time = event.time
		pthinfo = treeview.get_path_at_pos(x, y)
		if pthinfo is not None:
			path, col, cellx, celly = pthinfo
			treeview.grab_focus()
			treeview.set_cursor(path, col, 0)
			if event.button == 3:
    				selected,iter = treeview.get_selection().get_selected()
				#Por si hay un registro (malo) sin fecha, pa poder borrarlo
				try:
					date = self.parent.date.setDate(selected.get_value(iter,2))
				except:
					pass
				self.popup.show(selected.get_value(iter,0), event.button, time)
			elif event.button == 1:
				self.notebook.set_current_page(0)
				self.parent.refreshGraphView("record")
		logging.debug("<<")
		return False
	
	def actualize_recordTreeView(self, record_list):
		logging.debug(">>")
		iterOne = False
		store = gtk.TreeStore(
			gobject.TYPE_INT,          	#record_id
			gobject.TYPE_STRING,		#Time
			gobject.TYPE_STRING,		#Sport
			gobject.TYPE_STRING,		#Distance
			object)
		for i in record_list:
			#Get lap info 
			id_record = i[8]
			laps = self.parent.record.getLaps(id_record)
			iter = store.append(None)
			if not iterOne:
				iterOne = iter
			dateTime = i[12]
			if dateTime is not None:
				localTime = dateutil.parser.parse(dateTime).strftime("%H:%M")
			else:
				localTime = ""
			store.set (
				iter,
				0, int(i[8]),
				1, str(localTime),
				2, str(i[0]),
				3, str(i[2])
				)
			if laps is not None:
				for lap in laps:
					#"id_lap, record, elapsed_time, distance, start_lat, start_lon, end_lat, end_lon, calories, lap_number",  
					lapNumber = "%s%d" % ( _("lap"), int(lap[9])+1 ) 
					distance = "%0.2f" % (float(lap[3]) / 1000.0)
					timeHours = int(float(lap[2]) / 3600)
					timeMin = int((float(lap[2]) / 3600.0 - timeHours) * 60)
					timeSec = float(lap[2]) - (timeHours * 3600) - (timeMin * 60) 
					if timeHours > 0:
						duration = "%d%s%02d%s%02d%s" % (timeHours, _("h"), timeMin, _("m"), timeSec, _("s"))
					else:
						duration = "%2d%s%02d%s" % (timeMin, _("m"), timeSec, _("s"))

					child_iter = store.append(iter)
					store.set (
						child_iter,
						0, int(i[8]),
						1, lapNumber,
						2, duration,
						3, distance
						)
		self.recordTreeView.set_model(store)
		if iterOne:
			self.recordTreeView.get_selection().select_iter(iterOne)
		logging.debug("<<")
		#if len(record_list)>0:
	
	def parseFloat(self,string):
		try:
			return float(string)
		except:
			return float(0)

	def actualize_calendar(self,record_list):
		logging.debug(">>")
		self.calendar.clear_marks()
		for i in record_list:
			self.calendar.mark_day(int(i))
		logging.debug("<<")

	def on_about_activate(self,widget):
		aboutwindow = About(self.data_path, self.version)
		aboutwindow.run()

	def getSportSelected(self):
		sport = self.sportlist.get_active()
		if (sport > 0):
			return self.sportlist.get_active_text()
		else:
			return None

	def quit(self, *args):
		self.parent.quit()
		#sys.exit("Exit!")
		#self.parent.webservice.stop()
		#self.gtk_main_quit()

	def on_yearview_clicked(self,widget):
		self.notebook.set_current_page(2)
		self.selected_view="year"
		self.actualize_yearview()
	
	def on_recordTree_clicked(self,widget,num,num2):
		selected,iter = self.recordTreeView.get_selection().get_selected()
		self.parent.editRecord(selected.get_value(iter,0))

	######## waypoints events ##########
	def on_savewaypoint_clicked(self,widget):
		selected,iter = self.waypointTreeView.get_selection().get_selected()
		id_waypoint = selected.get_value(iter,0)
		lat = self.waypoint_latitude.get_text()
		lon = self.waypoint_longitude.get_text()
		name = self.waypoint_name.get_text()
		desc = self.waypoint_description.get_text()
		sym = self.waypoint_type.get_active_text()
		self.parent.updateWaypoint(id_waypoint,lat,lon,name,desc,sym)
	
	def on_removewaypoint_clicked(self,widget):
		selected,iter = self.waypointTreeView.get_selection().get_selected()
		id_waypoint = selected.get_value(iter,0)
		self.parent.removeWaypoint(id_waypoint)

	def on_hrpiebutton_clicked(self,widget):
		self.heartrate_vbox2.show()	
		self.heartrate_vbox.hide()	
	
	def on_hrplotbutton_clicked(self,widget):
		self.heartrate_vbox.show()	
		self.heartrate_vbox2.hide()	
