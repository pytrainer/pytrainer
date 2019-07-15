# -*- coding: utf-8 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net
#Copyright (C) Arto Jantunen <viiru@iki.fi>

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

from gi.repository import Gtk

class PopupMenu(Gtk.Menu):
    def __init__(self, data_path = None, parent = None):
        super(PopupMenu, self).__init__()
        self.windowmain = parent
        edit_record = Gtk.ImageMenuItem(Gtk.STOCK_EDIT)
        edit_record.set_label(_("Edit Record"))
        edit_record.connect("activate", self.on_editrecord_activate)
        self.attach(edit_record, 0, 1, 0, 1)
        show_graph = Gtk.ImageMenuItem(Gtk.STOCK_FIND)
        show_graph.set_label(_("Show graph in classic view"))
        show_graph.connect("activate", self.on_showclassic_activate)
        self.attach(show_graph, 0, 1, 1, 2)
        self.attach(Gtk.SeparatorMenuItem(), 0, 1, 2, 3)
        remove_record = Gtk.ImageMenuItem(Gtk.STOCK_DELETE)
        remove_record.connect("activate", self.on_remove_activate)
        self.attach(remove_record, 0, 1, 3, 4)
    
    def show(self,id_record,event_button, time, date=None):
        self.id_record = id_record
        self.date = date
        self.iter = iter
        self.show_all()
        self.popup_at_pointer(None)

    def on_editrecord_activate(self,widget):
        self.windowmain.parent.editRecord(self.id_record, view=self.windowmain.selected_view)

    def on_showclassic_activate(self,widget):
        #Set date in classic view
        if self.date is not None:
            self.windowmain.parent.date.setDate(self.date)
        self.windowmain.classicview_item.set_active(True)
        self.windowmain.notebook.set_current_page(0)
        self.windowmain.recordview.set_current_page(0)
        self.windowmain.parent.refreshRecordGraphView("info", id_record=self.id_record)

    def on_remove_activate(self,widget):
        self.windowmain.parent.removeRecord(self.id_record, view=self.windowmain.selected_view)
