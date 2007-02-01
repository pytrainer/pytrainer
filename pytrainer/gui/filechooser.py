# -*- coding: iso-8859-1 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net
# Jakinbidea & Grupo Ikusnet Developer
# vud1@grupoikusnet.com

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

class FileChooser(SimpleGladeApp):
	def __init__(self,data_path = None, parent = None, method = None, action = None):
		self.data_path = data_path
		self.filename = None
		self.parent = parent
		self.method = method
		root="filechooserdialog"
		SimpleGladeApp.__init__(self, data_path+"glade/pytrainer.glade", root, None)
		if (action == "open"):
			self.filechooserdialog.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
			filter = gtk.FileFilter()
			filter.set_name("gpx files")
			filter.add_pattern("*.gpx")
			self.filechooserdialog.set_filter(filter)
		else:
			self.filechooserdialog.set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
			self.filechooserdialog.set_current_name("*.csv")

	def on_accept_clicked(self,widget):
		self.filename = self.filechooserdialog.get_filename()
		parentmethod = getattr(self.parent,self.method)
		parentmethod()
		self.closewindow()
	
	def on_cancel_clicked(self,widget):
		self.closewindow()

	def closewindow(self):
		self.filechooserdialog.hide()
		self.filechooserdialog = None
		self.quit()	
