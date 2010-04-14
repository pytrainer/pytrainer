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

from SimpleGladeApp import SimpleGladeApp
from windowcalendar import WindowCalendar
import gtk
import gobject
import logging

class WindowProfile(SimpleGladeApp):
	def __init__(self, data_path = None, parent=None, pytrainer_main=None):
		glade_path="glade/profile.glade"
		root = "newprofile"
		domain = None
		self.parent = parent
		self.pytrainer_main = pytrainer_main
		self.data_path = data_path
		SimpleGladeApp.__init__(self, data_path+glade_path, root, domain)
		self.conf_options = [
			"prf_name",
			"prf_gender",
			"prf_weight",
			"prf_height",
			"prf_age",
			"prf_ddbb",
			"prf_ddbbhost",
			"prf_ddbbname",
			"prf_ddbbuser",
			"prf_ddbbpass",
			"prf_maxhr",
			"prf_minhr",
			"prf_hrzones_karvonen",
			"prf_us_system"
			]

	def new(self):
		self.gender_options = {
			0:_("Male"),
			1:_("Female")
			}

		self.ddbb_type = {
			0:"sqlite",
			1:"mysql"
			}
	
		#anhadimos las opciones al combobox gender
		for i in self.gender_options:
			self.prf_gender.insert_text(i,self.gender_options[i])
		
		#hacemos lo propio para el combobox ddbb
		for i in self.ddbb_type:
			self.prf_ddbb.insert_text(i,self.ddbb_type[i])

		#preparamos la lista sports:
		column_names=[_("Sport"),_("MET"),_("Extra Weight")]
		for column_index, column_name in enumerate(column_names):
			column = gtk.TreeViewColumn(column_name, gtk.CellRendererText(), text=column_index)
			column.set_resizable(True)
			self.sportTreeView.append_column(column)
					       
		
	def setValues(self,list_options):
		for i in self.conf_options:
			if not list_options.has_key(i):
				continue
			var = getattr(self,i)
			if i != "prf_gender" and i != "prf_ddbb" and i !="prf_hrzones_karvonen" and i!="prf_us_system":
				var.set_text(list_options[i])
			elif i == "prf_hrzones_karvonen" or i == "prf_us_system":
				if list_options[i]=="True":
					var.set_active(True)
			elif i == "prf_gender":
				for j in self.gender_options:
					if self.gender_options[j]==list_options[i]:
						var.set_active(j)
			elif i == "prf_ddbb":
				for j in self.ddbb_type:
					if self.ddbb_type[j]==list_options[i]:
						var.set_active(j)
						if j==0:
							self._ddbb_value_deactive()
						else:
							self._ddbb_value_active()
	
	def saveOptions(self):
		list_options = []
		for i in self.conf_options:
			var = getattr(self,i)
			if i != "prf_gender" and i != "prf_ddbb" and i != "prf_hrzones_karvonen" and i != "prf_us_system":
				list_options.append((i,var.get_text()))
			elif i == "prf_hrzones_karvonen" or i == "prf_us_system":
				if var.get_active():
					list_options.append((i,"True"))
				else:
					list_options.append((i,"False"))
			else:
				list_options.append((i,var.get_active_text()))
		self.parent.setProfile(list_options)
	
	def on_calendar_clicked(self,widget):
		calendardialog = WindowCalendar(self.data_path,self)
		calendardialog.run()

	def setDate(self,date):
		self.prf_age.set_text(date)

	def on_switch_page(self,widget,pointer,frame):
		#print widget, pointer, frame
		if frame==2:
			self.saveOptions()
			sport_list = self.parent.getSportList()
			if sport_list == 0:
				pass
			elif sport_list == -1:
				self.sportlistbutton.set_label("It is not possible connect to the server")
			else:
        			store = gtk.ListStore(
            				gobject.TYPE_STRING,
            				gobject.TYPE_STRING,
            				gobject.TYPE_STRING,
            				object)
				for i in sport_list:
					if not i[1]:
						met = i[1]
					else:
						met = 0
					if not i[2]:
						weight = i[2]
					else:
						weight = 0
                			iter = store.append()
                			store.set (
                    				iter,
                    				0, str(i[0]),
                    				1, i[1],
                    				2, i[2]
                    				)
        			self.sportTreeView.set_model(store)
				#self.sportlistbutton.hide()
				self.sportlist.show()
		elif frame == 4: #Startup Parameters page selected
			self.init_params_tab()
	
	def init_params_tab(self):
		#Show log level
		if self.pytrainer_main.startup_options.log_level == logging.ERROR:
			self.comboboxLogLevel.set_active(0)
		elif self.pytrainer_main.startup_options.log_level == logging.WARNING:
			self.comboboxLogLevel.set_active(1)
		elif self.pytrainer_main.startup_options.log_level == logging.INFO:
			self.comboboxLogLevel.set_active(2)
		elif self.pytrainer_main.startup_options.log_level == logging.DEBUG:
			self.comboboxLogLevel.set_active(3)
		else:
			self.comboboxLogLevel.set_active(0)
			print "Unknown logging level specified"

		#Show if validation requested
		if self.pytrainer_main.startup_options.validate:
			self.checkbuttonValidate.set_active(True)
		else:
			self.checkbuttonValidate.set_active(False)
			
		#Show if database and config check requested 
		if self.pytrainer_main.startup_options.check:
			self.checkbuttonCheck.set_active(True)
		else:
			self.checkbuttonCheck.set_active(False)
		
		#Show if using Googlemaps API v3
		if self.pytrainer_main.startup_options.gm3:
			self.checkbuttonGM3.set_active(True)
		else:
			self.checkbuttonGM3.set_active(False)
			
		#Show if unified import activated
		if self.pytrainer_main.startup_options.testimport:
			self.checkbuttonUnifiedImport.set_active(True)
		else:
			self.checkbuttonUnifiedImport.set_active(False)
		
	def on_comboboxLogLevel_changed(self, widget):
		active = self.comboboxLogLevel.get_active()
		if active == 1:
			logging.debug("Setting log level to WARNING")
			self.pytrainer_main.startup_options.log_level = logging.WARNING
		elif active == 2:
			logging.debug("Setting log level to INFO")
			self.pytrainer_main.startup_options.log_level = logging.INFO
		elif active == 3:
			logging.debug("Setting log level to DEBUG")
			self.pytrainer_main.startup_options.log_level = logging.DEBUG
		else:
			logging.debug("Setting log level to ERROR")
			self.pytrainer_main.startup_options.log_level = logging.ERROR
		self.pytrainer_main.set_logging_level(self.pytrainer_main.startup_options.log_level)	
		
	def on_checkbuttonValidate_toggled(self, widget):
		if self.checkbuttonValidate.get_active():
			logging.debug( "Validate activated")
			self.pytrainer_main.startup_options.validate = True
		else:
			logging.debug("Validate deactivated")
			self.pytrainer_main.startup_options.validate = False
			
	def on_checkbuttonCheck_toggled(self, widget):
		if self.checkbuttonCheck.get_active():
			logging.debug( "Check activated")
			if self.pytrainer_main.startup_options.check is not True:
				#Need to do sanitycheck
				logging.debug("Need to do sanitycheck")
				self.pytrainer_main.sanityCheck()
			self.pytrainer_main.startup_options.check = True
		else:
			logging.debug("Check deactivated")
			self.pytrainer_main.startup_options.check = False
			
	def on_checkbuttonGM3_toggled(self, widget):
		if self.checkbuttonGM3.get_active():
			logging.debug("GM3 activated")
			self.pytrainer_main.startup_options.gm3 = True
		else:
			logging.debug("GM3 deactivated")
			self.pytrainer_main.startup_options.gm3 = False
	
	def on_checkbuttonUnifiedImport_toggled(self, widget):
		if self.checkbuttonUnifiedImport.get_active():
			logging.debug("Unified Import activated")
			if self.pytrainer_main.startup_options.testimport is not True:
				#Need to enable unified import
				logging.debug("Need to enable unified import")
				self.pytrainer_main.windowmain.set_unified_import(True)
			else:
				#No change 
				logging.debug("No change to unified import")
		else:
			logging.debug("Unified Import deactivated")
			if self.pytrainer_main.startup_options.testimport is True:
				logging.debug("Need to deactivate unified import")
				self.pytrainer_main.windowmain.set_unified_import(False)
			else:
				logging.debug("No change to unified import")
	
	def on_sportlistbutton_clicked(self,widget):
		sport_list = self.parent.getSportList()
		if sport_list == 0:
			self.parent.build_ddbb()
			self.sportlistbutton.hide()
			self.sportlist.show()
		
			
	def on_accept_clicked(self,widget):
		self.saveOptions()
		self.close_window()
	
	def on_cancel_clicked(self,widget):
		self.close_window()

	def close_window(self):
		self.newprofile.hide()
		self.newprofile = None
		self.quit()

	def _ddbb_value_active(self):
		self.prf_ddbbhost_label.set_sensitive(1)
		self.prf_ddbbname_label.set_sensitive(1)
		self.prf_ddbbuser_label.set_sensitive(1)
		self.prf_ddbbpass_label.set_sensitive(1)
		self.prf_ddbbhost.set_sensitive(1)
		self.prf_ddbbname.set_sensitive(1)
		self.prf_ddbbuser.set_sensitive(1)
		self.prf_ddbbpass.set_sensitive(1)
	
	def _ddbb_value_deactive(self):
		self.prf_ddbbhost_label.set_sensitive(0)
		self.prf_ddbbname_label.set_sensitive(0)
		self.prf_ddbbuser_label.set_sensitive(0)
		self.prf_ddbbpass_label.set_sensitive(0)
		self.prf_ddbbhost.set_sensitive(0)
		self.prf_ddbbname.set_sensitive(0)
		self.prf_ddbbuser.set_sensitive(0)
		self.prf_ddbbpass.set_sensitive(0)

	def on_prf_ddbb_changed(self,widget):
		i = self.prf_ddbb.get_active_text()
		if i == "mysql":
			self._ddbb_value_active()
		else:
			self._ddbb_value_deactive()

	def on_addsport_clicked(self,widget):
		self.hidesportsteps()
		self.buttonbox.set_sensitive(0)
		self.addsport.show()

	def on_newsport_accept_clicked(self,widget):
		sport = self.newsportentry.get_text()
		met = self.newmetentry.get_text()
		weight = self.newweightentry.get_text()
		self.parent.addNewSport(sport,met,weight)
		self.parent.actualize_mainsportlist()
		self.on_switch_page(None,None,2)
		self.hidesportsteps()
		self.buttonbox.set_sensitive(1)
		self.sportlist.show()

	def on_delsport_clicked(self,widget):
		selected,iter = self.sportTreeView.get_selection().get_selected()
		if iter:
			self.buttonbox.set_sensitive(0)
			sport = selected.get_value(iter,0)
			self.sportnamedel.set_text(sport)
			self.hidesportsteps()
			self.deletesport.show()

	def on_deletesport_clicked(self,widget):
		sport = self.sportnamedel.get_text()
		self.parent.delSport(sport)
		self.parent.actualize_mainsportlist()
		self.on_switch_page(None,None,2)
		self.hidesportsteps()
		self.buttonbox.set_sensitive(1)
		self.sportlist.show()
	
	def on_editsport_clicked(self,widget):
		self.buttonbox.set_sensitive(0)
		selected,iter = self.sportTreeView.get_selection().get_selected()
		if iter:
			sport = selected.get_value(iter,0)
			name,met,weight = self.parent.getSportInfo(sport)
			self.editsportentry.set_text(sport)
			self.sportnameedit.set_text(sport)
			self.editweightentry.set_text(str(weight))
			self.editmetentry.set_text(str(met))
			self.hidesportsteps()
			self.editsport.show()
	
	def on_editsport_accept_clicked(self,widget):
		oldnamesport = self.sportnameedit.get_text()
		newnamesport = self.editsportentry.get_text()
		newmetsport = self.editmetentry.get_text()
		newweightsport = self.editweightentry.get_text()
		self.parent.updateSport(oldnamesport,newnamesport,newmetsport,newweightsport)
		self.parent.actualize_mainsportlist()
		self.on_switch_page(None,None,2)
		self.hidesportsteps()
		self.buttonbox.set_sensitive(1)
		self.sportlist.show()
		
	def on_sportcancel_clicked(self,widget):
		self.hidesportsteps()
		self.buttonbox.set_sensitive(1)
		self.sportlist.show()

	def on_calculatemaxhr_clicked(self,widget=None):
		import datetime
		today = "%s"%datetime.date.today()
		year1,month1,day1 = today.split("-")
		year2,month2,day2 = self.prf_age.get_text().split("-")
		diff = datetime.datetime(int(year1), int(month1), int(day1),0,0,0) - datetime.datetime(int(year2), int(month2), int(day2),0,0,0)
		self.prf_maxhr.set_text("%d" %(220-int(diff.days/365)))

	def hidesportsteps(self):
		self.sportlist.hide()
		self.addsport.hide()
		self.deletesport.hide()
		self.editsport.hide()	
