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

import gobject

from SimpleGladeApp import *
from popupmenu import PopupMenu
from aboutdialog import About

from pytrainer.lib.date import Date
from pytrainer.lib.system import checkConf
from pytrainer.lib.xmlUtils import XMLParser

class Main(SimpleGladeApp):
	def __init__(self, data_path = None, parent = None, version = None):
		self.version = version
		self.parent = parent
		self.data_path = data_path
		glade_path="glade/pytrainer.glade"
		root = "window1"
		domain = None
		SimpleGladeApp.__init__(self, self.data_path+glade_path, root, domain)

		self.popup = PopupMenu(data_path,self)
		self.block = False

	def new(self):
		self.menublocking = 0
		self.selected_view="day"
		self.window1.set_title ("pyTrainer %s" % self.version)
		self.record_list = []
		#create the columns for the listdayrecord
		column_names=[_("id"),_("Sport"),_("Kilometer")]
		self.create_treeview(self.recordTreeView,column_names)
		#create the columns for the listarea
		column_names=[_("id"),_("Title"),_("Date"),_("Distance"),_("Sport"),_("Time"),_("Beats"),_("Average"),("Calories")]
		self.create_treeview(self.allRecordTreeView,column_names)
		self.create_menulist(column_names)
		conf = checkConf()
                self.fileconf = conf.getValue("confdir")+"/listviewmenu.xml"
		if not os.path.isfile(self.fileconf):
			self._createXmlListView(self.fileconf)
		self.showAllRecordTreeViewColumns()
		self.allRecordTreeView.set_search_column(1)
	
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

	def addImportPlugin(self,plugin):
		button = gtk.MenuItem(plugin[0])
		button.connect("activate", self.parent.runPlugin, plugin[1])
		self.menuitem1_menu.insert(button,2)
		self.menuitem1_menu.show_all()

	def addExtension(self,extension):
		txtbutton,extensioncode,extensiontype = extension
		button = gtk.Button(txtbutton)
		button.connect("button_press_event", self.runExtension, extension)
		self.recordbuttons_hbox.pack_start(button,False,False,0)
		self.recordbuttons_hbox.show_all()

	def runExtension(self,widget,widget2,extension):
		txtbutton,extensioncode,extensiontype = extension
		if extensiontype=="record":
    			selected,iter = self.recordTreeView.get_selection().get_selected()
			id = selected.get_value(iter,0)
		self.parent.runExtension(extension,id)

	def window_sensitive(self, value):
		self.window1.set_sensitive(value)
	
	def createGraphs(self,RecordGraph,DayGraph,MonthGraph,YearGraph):
		self.drawarearecord = RecordGraph(self.record_vbox, self.record_combovalue)
		#self.drawareaday = DayGraph(self.day_vbox, self.day_combovalue)
		self.day_vbox.hide()
		self.drawareamonth = MonthGraph(self.month_vbox, self.month_combovalue)
		self.drawareayear = YearGraph(self.year_vbox, self.year_combovalue)
	
	def createMap(self,Googlemaps):
		self.googlemaps = Googlemaps(self.data_path, self.map_vbox)

	def updateSportList(self,listSport):
		self.sportlist.set_active(1)
		while (self.sportlist.get_active() == 1):
			self.sportlist.remove_text(1)
			self.sportlist.set_active(1)
		
		for i in listSport:
			self.sportlist.append_text(i[0])
			self.sportlist.set_active(0)

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
		if len(record_list)>0:
			record_list=record_list[0]
			
			self.recordview.set_sensitive(1)
			distance = self.parseFloat(record_list[2])
			beats = self.parseFloat(record_list[4])
			average = self.parseFloat(record_list[6])
			calories = self.parseFloat(record_list[7])
			upositive = self.parseFloat(record_list[10])
			unegative = self.parseFloat(record_list[11])
			title = str(record_list[9])
			comments = str(record_list[5])
			
			self.record_distance.set_text("%0.2f" %distance)
			hour,min,sec=self.parent.date.second2time(int(record_list[3]))
			self.record_hour.set_text("%d" %hour)
			self.record_minute.set_text("%d" %min)
			self.record_second.set_text("%d" %sec)
			self.record_beats.set_text("%0.2f" %beats)
			self.record_average.set_text("%0.2f" %average)
			self.record_calories.set_text("%0.2f" %calories)
			self.record_upositive.set_text("%0.2f" %upositive)
			self.record_unegative.set_text("%0.2f" %unegative)
			self.record_title.set_text(title)
			buffer = self.record_comments.get_buffer()
                	start,end = buffer.get_bounds()
                	buffer.set_text(comments)

		else:
			self.recordview.set_sensitive(0)
	
	def actualize_recordgraph(self,record_list):
		if len(record_list)>0:
			self.record_vbox.set_sensitive(1)
		else:
			self.record_vbox.set_sensitive(0)
		self.drawarearecord.drawgraph(record_list)

	def actualize_dayview(self,record_list):
		if len(record_list)>0:
			record_list=record_list[0]
			
			distance = self.parseFloat(record_list[2])
			beats = self.parseFloat(record_list[4])
			average = self.parseFloat(record_list[6])
			calories = self.parseFloat(record_list[7])
			
			self.dayview.set_sensitive(1)
			self.day_distance.set_text("%0.2f" %distance)
			hour,min,sec=self.parent.date.second2time(int(record_list[3]))
			self.day_hour.set_text("%d" %hour)
			self.day_minute.set_text("%d" %min)
			self.day_second.set_text("%d" %sec)
			self.day_beats.set_text("%0.2f" %beats)
			self.day_average.set_text("%0.2f" %average)
			self.day_calories.set_text("%0.2f" %calories)
			self.day_topic.set_text(record_list[1])
			
		else:
			self.dayview.set_sensitive(0)
	
	def actualize_daygraph(self,record_list):
		if len(record_list)>0:
			self.day_vbox.set_sensitive(1)
		else:
			self.day_vbox.set_sensitive(0)
		self.drawareaday.drawgraph(record_list)
	
	def actualize_map(self,id_record):
		self.googlemaps.drawMap(id_record)
	
	def actualize_monthview(self,record_list, nameMonth):
		self.month_date.set_text(nameMonth)
		km = calories = time = average = beats = 0
		num_records = len(record_list)
	
		if num_records>0:
			for record in record_list:
				km += self.parseFloat(record[1])
				time += self.parseFloat(record[2])
				average += self.parseFloat(record[5])
				calories += self.parseFloat(record[6])
				beats += self.parseFloat(record[3])
			self.montht_distance.set_text("%0.3f" %km)
			self.montha_distance.set_text("%0.3f" %(km/num_records))
			hour,min,sec = self.parent.date.second2time(time)
			self.montht_hour.set_text("%d" %hour)
			self.montht_minute.set_text("%d" %min)
			self.montht_second.set_text("%d" %sec)
			hour,min,sec = self.parent.date.second2time(time/num_records)
			self.montha_hour.set_text("%d" %hour)
			self.montha_minute.set_text("%d" %min)
			self.montha_second.set_text("%d" %sec)
			self.montha_beats.set_text("%0.3f" %(beats/num_records))
			self.montha_average.set_text("%0.3f" %(average/num_records))
			self.montha_calories.set_text("%0.3f" %(calories/num_records))
			self.monthview.set_sensitive(1)
		else:
			self.monthview.set_sensitive(0)

	def actualize_monthgraph(self,record_list):
		self.drawareamonth.drawgraph(record_list)
	
	def actualize_yearview(self,record_list, year):
		self.year_date.set_text("%d" %int(year))
		km = calories = time = average = beats = 0
		num_records = len(record_list)
		if num_records>0:
			for record in record_list:
				km += self.parseFloat(record[1])
				time += self.parseFloat(record[2])
				average += self.parseFloat(record[5])
				calories += self.parseFloat(record[6])
				beats += self.parseFloat(record[3])
			self.yeart_distance.set_text("%0.3f" %km)
			self.yeara_distance.set_text("%0.3f" %(km/num_records))
			hour,min,sec = self.parent.date.second2time(time)
			self.yeart_hour.set_text("%d" %hour)
			self.yeart_minute.set_text("%d" %min)
			self.yeart_second.set_text("%d" %sec)
			hour,min,sec = self.parent.date.second2time(time/num_records)
			self.yeara_hour.set_text("%d" %hour)
			self.yeara_minute.set_text("%d" %min)
			self.yeara_second.set_text("%d" %sec)
			self.yeara_beats.set_text("%0.3f" %(beats/num_records))
			self.yeara_average.set_text("%0.3f" %(average/num_records))
			self.yeara_calories.set_text("%0.3f" %(calories/num_records))
			self.yearview.set_sensitive(1)
		else:
			self.yearview.set_sensitive(0)
			self.drawareayear.drawgraph([])
	
	def actualize_yeargraph(self,record_list):
		self.drawareayear.drawgraph(record_list)

	def actualize_listview(self,record_list):
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

	######################
	## Lista de eventos ##
	######################

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
		self.parent.refreshGraphView(self.selected_view)
	
	def on_page_change(self,widget,gpointer,page):
		if page == 0:
			self.selected_view="record"
		elif page == 1:
			self.selected_view="day"
		elif page == 2:
			self.selected_view="month"
		elif page == 3:
			self.selected_view="year"
		self.parent.refreshGraphView(self.selected_view)
	
	def on_showmap_clicked(self,widget):
		self.infoarea.hide()
		self.maparea.show()
		self.parent.refreshMapView()
	
	def on_hidemap_clicked(self,widget):
		self.maparea.hide()
		self.infoarea.show()
	
	def on_day_combovalue_changed(self,widget):
		self.parent.refreshGraphView(self.selected_view)
	
	def on_month_combovalue_changed(self,widget):
		self.parent.refreshGraphView(self.selected_view)
	
	def on_year_combovalue_changed(self,widget):
		self.parent.refreshGraphView(self.selected_view)
	
	def on_calendar_selected(self,widget):
		if self.block:
			self.block = False
		else:
			self.notebook.set_current_page(1)
			self.selected_view="day"
			self.parent.refreshListRecords()
			self.parent.refreshGraphView(self.selected_view)

	def on_calendar_changemonth(self,widget):
		self.block = True
		self.notebook.set_current_page(2)
		self.selected_view="month"
		self.parent.refreshListRecords()
		self.parent.refreshGraphView(self.selected_view)
	
	def on_calendar_next_year(self,widget):
		self.block = True
		self.notebook.set_current_page(3)
		self.selected_view="year"
		self.parent.refreshListRecords()
		self.parent.refreshGraphView(self.selected_view)
	
	def on_classicview_activate(self,widget):
		self.listarea.hide()
		self.classicarea.show()
	
	def on_listview_activate(self,widget):
		self.classicarea.hide()
		self.parent.refreshListView()
		self.listarea.show()
	
	def on_extensions_activate(self,widget):
		self.parent.editExtensions()

	def on_gpsplugins_activate(self,widget):
		self.parent.editGpsPlugins()
	#hasta aqui revisado
	def on_allRecordTreeView_button_press(self, treeview, event):
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
		return False
	
	def actualize_recordTreeView(self, record_list):
		iterOne = False
		store = gtk.ListStore(
			gobject.TYPE_INT,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			object)
		for i in record_list:
			iter = store.append()
			if not iterOne:
				iterOne = iter
			store.set (
				iter,
				0, int(i[8]),
				1, str(i[0]),
				2, str(i[2])
				)
		self.recordTreeView.set_model(store)
		if iterOne:
			self.recordTreeView.get_selection().select_iter(iterOne)
		#if len(record_list)>0:
	
	def parseFloat(self,string):
		try:
			return float(string)
		except:
			return float(0)

	def actualize_calendar(self,record_list):
		self.calendar.clear_marks()
		for i in record_list:
			self.calendar.mark_day(int(i))

	def on_about_activate(self,widget):
		aboutwindow = About(self.data_path, self.version)
		aboutwindow.run()

	def getSportSelected(self):
		sport = self.sportlist.get_active()
		if (sport > 0):
			return self.sportlist.get_active_text()
		else:
			return -1

	def quit(self, *args):
		self.gtk_main_quit()

	def on_yearview_clicked(self,widget):
		self.notebook.set_current_page(2)
		self.selected_view="year"
		self.actualize_yearview()
	
	def on_recordTree_clicked(self,widget,num,num2):
    		selected,iter = self.recordTreeView.get_selection().get_selected()
		self.parent.editRecord(selected.get_value(iter,0))
	
