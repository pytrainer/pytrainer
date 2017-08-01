# SimpleGladeApp.py
# Module that provides an object oriented abstraction to pygtk and libglade.
# Copyright (C) 2004 Sandino Flores Moreno

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

import os
import sys
import gtk
from pytrainer.environment import Environment

class SimpleBuilderApp(dict):
    def __init__(self, ui_filename):
        self._builder = gtk.Builder()
        env = Environment()
        file_path = os.path.join(env.glade_dir, ui_filename)
        self._builder.add_from_file(file_path)
        self._builder.connect_signals(self)
        self.new()

    def signal_autoconnect(self):
        signals = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr):
                signals[attr_name] = attr
        self._builder.connect_signals(signals)

    def __getattr__(self, data_name):
        if data_name in self:
            data = self[data_name]
            return data
        else:
            widget = self._builder.get_object(data_name)
            if widget != None:
                self[data_name] = widget
                return widget
            else:
                raise AttributeError, data_name

    def __setattr__(self, name, value):
        self[name] = value

    def new(self):
        pass

    def on_keyboard_interrupt(self):
        pass

    def gtk_widget_show(self, widget, *args):
        widget.show()

    def gtk_widget_hide(self, widget, *args):
        widget.hide()

    def gtk_widget_grab_focus(self, widget, *args):
        widget.grab_focus()

    def gtk_widget_destroy(self, widget, *args):
        widget.destroy()

    def gtk_window_activate_default(self, widget, *args):
        widget.activate_default()

    def gtk_true(self, *args):
        return gtk.TRUE

    def gtk_false(self, *args):
        return gtk.FALSE

    def gtk_main_quit(self, *args):
        gtk.main_quit()

    def main(self):
        gtk.main()

    def quit(self, widget=None):
        gtk.main_quit()

    def run(self):
        try:
            self.main()
        except KeyboardInterrupt:
            self.on_keyboard_interrupt()

    def create_treeview(self,treeview,column_names):
        i=0
        for column_index, column_name in enumerate(column_names):
            column = gtk.TreeViewColumn(column_name, gtk.CellRendererText(), text=column_index)
            column.set_resizable(True)
            if i==0:
                column.set_visible(False)
            column.set_sort_column_id(i)
            treeview.append_column(column)

