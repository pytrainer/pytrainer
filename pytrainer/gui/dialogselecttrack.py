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
import gobject

class DialogSelectTrack(SimpleGladeApp):
	def __init__(self, data_path = None, tracks = None, okmethod = None, gpx = None):
		self.data_path = data_path
		self.okmethod = okmethod
		self.tracks = tracks
		self.gpx = gpx
		root="selecttrackdialog"
		SimpleGladeApp.__init__(self, data_path+"glade/pytrainer.glade", root, None)

	def new(self):		
		#preparamos la lista con los tracks disponibles:
                column_names=[_("Track Name"), _("Date")]
		self.create_treeview(self.trkpTreeView,column_names)
		self.actualize_treeview(self.trkpTreeView,self.tracks)

	def on_ok_clicked(self,widget):
		selected,iter = self.trkpTreeView.get_selection().get_selected()
                if iter:
                	trackname = selected.get_value(iter,0)
		self.okmethod(self.gpx,trackname)
		self.closewindow()
	
	def on_cancel_clicked(self,widget):
		self.closewindow()

	def closewindow(self):
		self.selecttrackdialog.hide()
		#self.selecttrackdialog = None
		self.quit()	
	
	def create_treeview(self,treeview,column_names):
		i=0
		for column_index, column_name in enumerate(column_names):
			column = gtk.TreeViewColumn(column_name, gtk.CellRendererText(), text=column_index)
			column.set_resizable(True)
			column.set_sort_column_id(i)
			treeview.append_column(column)
			i+=1
	
	def actualize_treeview(self, treeview, record_list):
		iterOne = False
	        store = gtk.ListStore(
	                gobject.TYPE_STRING,
	                gobject.TYPE_STRING,
	                object)
        
		for i in record_list:
	                iter = store.append()
	                if not iterOne:
	                        iterOne = iter
	                store.set (
	                        iter,
	                        0, str(i[0]),
	                        1, str(i[1])
	                        )
	        treeview.set_model(store)
	        if iterOne:
	                treeview.get_selection().select_iter(iterOne)
	
