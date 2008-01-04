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
import os

class WindowPlugins(SimpleGladeApp):
	def __init__(self, data_path = None, parent=None):
		glade_path="glade/pytrainer.glade"
		root = "plugins"
		domain = None
		self.parent = parent
		SimpleGladeApp.__init__(self, data_path+glade_path, root, domain)
	def new(self):
		column_names=["id","name"]
		self.create_treeview(self.pluginsTreeview,column_names)

	def setList(self, list):
		iterOne = False
		store = gtk.ListStore(
			gobject.TYPE_STRING,
			gobject.TYPE_STRING
			)
		for i in list:
			iter = store.append()
			if not iterOne:
				iterOne = iter
			store.set (iter, 
				0, i[0],
				1, i[1]
				)
		self.pluginsTreeview.set_model(store)
		if iterOne:
			self.pluginsTreeview.get_selection().select_iter(iterOne)
		self.on_pluginsTree_clicked(None,None)
	
	def create_treeview(self,treeview,column_names):
		i=0
		for column_index, column_name in enumerate(column_names):
			column = gtk.TreeViewColumn(column_name, gtk.CellRendererText(), text=column_index)
			if i==0:
				column.set_visible(False)
			treeview.append_column(column)
			i+=1

	def on_pluginsTree_clicked(self,widget,widget2):
		print "clicked"
		selected,iter = self.pluginsTreeview.get_selection().get_selected()
		print iter
		print selected.get_value(iter,0)
		name,description,status = self.parent.getPluginInfo(selected.get_value(iter,0))
		self.nameEntry.set_text(name)
		self.descriptionEntry.set_text(description)
		if int(status) > 0:
			self.statusEntry.set_text(_("Enable"))
		else:
			self.statusEntry.set_text(_("Disable"))

	def on_preferences_clicked(self,widget):
		selected,iter = self.pluginsTreeview.get_selection().get_selected()
		name,description,status = self.parent.getPluginInfo(selected.get_value(iter,0))
		prefs = self.parent.getPluginConfParams(selected.get_value(iter,0))
		
		self.prefwindow = gtk.Window()
		self.prefwindow.set_border_width(20)
  	    	self.prefwindow.set_title(_("%s settings" %name))
          	
		table = gtk.Table(1,2)
		i=0
		self.entryList = []
		for pref in prefs:
			label = gtk.Label("<b>%s</b>"%pref[0])
			label.set_use_markup(True)
			if pref[0] != "status":
				entry = gtk.Entry()
				entry.set_text(pref[1])
				self.entryList.append(entry)	
				table.attach(entry,1,2,i,i+1)
			else:
				combobox = gtk.combo_box_new_text()
				combobox.append_text(_("Disable"))	
				combobox.append_text(_("Enable"))	
				combobox.set_active(int(pref[1]))
				table.attach(combobox,1,2,i,i+1)
				self.entryList.append(combobox)	
			table.attach(label,0,1,i,i+1)
			i+=1
				
		button = gtk.Button(_("Ok"))
		button.connect("clicked", self.on_acceptSettings_clicked, None)
		table.attach(button,0,2,i,i+1)
          	self.prefwindow.add(table)
          	self.prefwindow.show_all()
	
	def on_acceptSettings_clicked(self, widget, widget2):
		selected,iter = self.pluginsTreeview.get_selection().get_selected()
		prefs = self.parent.getPluginConfParams(selected.get_value(iter,0))
		savedOptions = []
		i = 0
		for pref in prefs:
			try:
				savedOptions.append((pref[0],self.entryList[i].get_text()))
			except:
				combobox = self.entryList[i]
        			index = combobox.get_active()
				savedOptions.append((pref[0],"%s" %index))
			i+=1
		self.prefwindow.hide()
		self.prefwindow = None
		self.parent.setPluginConfParams(selected.get_value(iter,0),savedOptions)
		self.on_pluginsTree_clicked(None,None)

	def on_accept_clicked(self,widget):
		self.plugins.hide()
		self.plugins = None
		self.quit()
