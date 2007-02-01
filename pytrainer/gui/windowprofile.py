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
import gtk
import gobject

class WindowProfile(SimpleGladeApp):
	def __init__(self, data_path = None, parent=None):
		glade_path="glade/pytrainer.glade"
		root = "newprofile"
		domain = None
		self.parent = parent
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
			"prf_ddbbpass"]

	def new(self):
		self.gender_options = {
			0:"Male",
			1:"Female"
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
		column_names=["Sport"]
		for column_index, column_name in enumerate(column_names):
			column = gtk.TreeViewColumn(column_name, gtk.CellRendererText(), text=column_index)
			self.sportTreeView.append_column(column)
					       
		
	def setValues(self,list_options):
		for i in self.conf_options:
			var = getattr(self,i)
			if i != "prf_gender" and i != "prf_ddbb":
				var.set_text(list_options[i])
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
			if i != "prf_gender" and i != "prf_ddbb":
				list_options.append((i,var.get_text()))
			else:
				list_options.append((i,var.get_active_text()))
		self.parent.setProfile(list_options)

	def on_switch_page(self,widget,pointer,frame):
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
            				object)
				for i in sport_list:
                			iter = store.append()
                			store.set (
                    				iter,
                    				0, i[0]
                    				)
        			self.sportTreeView.set_model(store)
				#self.sportlistbutton.hide()
				self.sportlist.show()
	
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
		self.prf_ddbbhost.set_sensitive(1)
		self.prf_ddbbname.set_sensitive(1)
		self.prf_ddbbuser.set_sensitive(1)
		self.prf_ddbbpass.set_sensitive(1)
	
	def _ddbb_value_deactive(self):
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
		self.parent.addNewSport(sport)
		self.parent.actualize_mainsportlist()
		self.on_switch_page(None,None,2)
		self.hidesportsteps()
		self.buttonbox.set_sensitive(1)
		self.sportlist.show()

	def on_delsport_clicked(self,widget):
		self.buttonbox.set_sensitive(0)
		selected,iter = self.sportTreeView.get_selection().get_selected()
		try:
			sport = selected.get_value(iter,0)
			self.sportnamedel.set_text(sport)
			self.hidesportsteps()
			self.deletesport.show()
		except:
			pass

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
		try:
			sport = selected.get_value(iter,0)
			self.sportnameedit.set_text(sport)
			self.editsportentry.set_text(sport)
			self.hidesportsteps()
			self.editsport.show()
		except:
			pass
	
	def on_editsport_accept_clicked(self,widget):
		oldnamesport = self.sportnameedit.get_text()
		newnamesport = self.editsportentry.get_text()
		self.parent.updateSport(oldnamesport,newnamesport)
		self.parent.actualize_mainsportlist()
		self.on_switch_page(None,None,2)
		self.hidesportsteps()
		self.buttonbox.set_sensitive(1)
		self.sportlist.show()
		
	def on_sportcancel_clicked(self,widget):
		self.hidesportsteps()
		self.buttonbox.set_sensitive(1)
		self.sportlist.show()

	def hidesportsteps(self):
		self.sportlist.hide()
		self.addsport.hide()
		self.deletesport.hide()
		self.editsport.hide()	
