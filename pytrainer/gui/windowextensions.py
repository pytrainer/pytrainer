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

from .SimpleGladeApp import SimpleBuilderApp
from gi.repository import Gtk
from gi.repository import GObject
import io
from pytrainer.lib.localization import gtk_str

class WindowExtensions(SimpleBuilderApp):
    def __init__(self, data_path = None, parent=None):
        self.parent = parent
        SimpleBuilderApp.__init__(self, "extensions.ui")

    def new(self):
        column_names=["id","name"]
        self.create_treeview(self.extensionsTree,column_names)

    def setList(self, list):
        iterOne = False
        store = Gtk.ListStore(
                GObject.TYPE_STRING,
                GObject.TYPE_STRING
                )
        for i in list:
            iter = store.append()
            if not iterOne:
                iterOne = iter
            store.set (iter,
                    0, i[0],
                    1, i[1]
                    )
        self.extensionsTree.set_model(store)
        if iterOne:
            self.extensionsTree.get_selection().select_iter(iterOne)
        self.on_extensionsTree_clicked(None,None)

    def create_treeview(self,treeview,column_names):
        i=0
        for column_index, column_name in enumerate(column_names):
            column = Gtk.TreeViewColumn(column_name, Gtk.CellRendererText(), text=column_index)
            if i==0:
                column.set_visible(False)
            treeview.append_column(column)
            i+=1

    def on_extensionsTree_clicked(self,widget,widget2):
        selected,iter = self.extensionsTree.get_selection().get_selected()
        name,description,status,helpfile,type = self.parent.getExtensionInfo(selected.get_value(iter,0))
        self.nameEntry.set_text(name)
        self.descriptionEntry.set_text(description)
        if status is None or int(status) == 0:
            self.statusEntry.set_text(_("Disable"))
        else:
            self.statusEntry.set_text(_("Enable"))

    def on_preferences_clicked(self,widget):
        selected,iter = self.extensionsTree.get_selection().get_selected()
        name,description,status,helpfile,type = self.parent.getExtensionInfo(selected.get_value(iter,0))
        prefs = self.parent.getExtensionConfParams(selected.get_value(iter,0))

        self.prefwindow = Gtk.Window()
        self.prefwindow.set_border_width(20)
        self.prefwindow.set_title(_("%s settings" %name))
        self.prefwindow.set_modal(True)

        table = Gtk.Table(1,2)
        i=0
        self.entryList = []
        #print prefs
        for key in prefs.keys():
            #print key, prefs[key]
            label = Gtk.Label(label="<b>%s</b>"%key)
            label.set_use_markup(True)
            if key != "status":
                entry = Gtk.Entry()
                if prefs[key] is None:
                    entry.set_text("")
                else:
                    entry.set_text(prefs[key])
                self.entryList.append(entry)
                table.attach(entry,1,2,i,i+1)
            else:
                combobox = Gtk.ComboBoxText()
                combobox.append_text("Disable")
                combobox.append_text("Enable")
                if prefs[key] is None:
                    combobox.set_active(0)
                else:
                    combobox.set_active(int(prefs[key]))
                table.attach(combobox,1,2,i,i+1)
                self.entryList.append(combobox)
            table.attach(label,0,1,i,i+1)
            i+=1

        button = Gtk.Button(_("OK"))
        button.connect("clicked", self.on_acceptSettings_clicked, None)
        table.attach(button,0,2,i,i+1)
        self.prefwindow.add(table)
        self.prefwindow.show_all()

    def on_help_clicked(self,widget):
        selected,iter = self.extensionsTree.get_selection().get_selected()
        name,description,status,helpfile,type = self.parent.getExtensionInfo(selected.get_value(iter,0))
        with io.open(helpfile, encoding='utf-8') as input_file:
            text = input_file.read(2000)
        helpwindow = Gtk.Window()
        button = Gtk.Button(_("OK"))
        button.connect("clicked", self.on_accepthelp_clicked, helpwindow)
        vbox = Gtk.VBox()
        buffer = Gtk.TextBuffer()
        buffer.set_text(text)
        textview = Gtk.TextView()
        textview.set_buffer(buffer)
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.add(textview)
        vbox.pack_start(scrolledwindow, True, True, 0)
        vbox.pack_start(button, False, False, 0)
        helpwindow.add(vbox)
        helpwindow.resize(550,300)
        helpwindow.show_all()

    def on_accepthelp_clicked(self,widget,window):
        window.hide()
        window = None

    def on_acceptSettings_clicked(self, widget, widget2):
        selected,iter = self.extensionsTree.get_selection().get_selected()
        prefs = self.parent.getExtensionConfParams(selected.get_value(iter,0))
        savedOptions = []
        i = 0
        for key in prefs.keys():
            try:
                savedOptions.append((key, gtk_str(self.entryList[i].get_text())))
            except:
                combobox = self.entryList[i]
                index = combobox.get_active()
                savedOptions.append((key,"%s" %index))
            i+=1
        self.prefwindow.hide()
        self.prefwindow = None
        self.parent.setExtensionConfParams(selected.get_value(iter,0),savedOptions)
        self.on_extensionsTree_clicked(None,None)

    def on_accept_clicked(self,widget):
        self.extensions.hide()
        self.extensions = None
        self.quit()
