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

class PopupMenu(SimpleGladeApp):
	def __init__(self, data_path = None, parent = None):
		self.parent = parent
		glade_path="glade/pytrainer.glade"
		root = "popup"
		domain = None
		SimpleGladeApp.__init__(self, data_path+glade_path, root, domain)
	
	def show(self,id_record,event_button, time):
		self.id_record = id_record
		self.popup.popup( None, None, None, event_button, time)

	def on_editrecord_activate(self,widget):
		self.parent.parent.editRecord(self.id_record)

	def on_showclassic_activate(self,widget):
		self.parent.classicview_item.set_active(True)
		#self.parent.on_calendar_selected(None)
		self.parent.notebook.set_current_page(0)
		self.parent.parent.refreshGraphView("record")

	def on_remove_activate(self,widget):
		self.parent.parent.removeRecord(self.id_record)
