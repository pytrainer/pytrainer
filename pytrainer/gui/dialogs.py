#!/usr/bin/env python

#Copyright (C)

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

import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import logging

class fileChooserDialog():
    def __init__(self, title = "Choose a file", multiple = False):
        logging.warning("Deprecated fileChooserDialog class called")
        self.inputfiles = open_file_chooser_dialog(title=title, multiple=multiple)

    def getFiles(self):
        return self.inputfiles

class guiFlush():
    def __init__(self):
        dialog = Gtk.Dialog(title=None, parent=None, flags=0, buttons=None)
        dialog.show()
        dialog.destroy()

def open_file_chooser_dialog(title="Choose a file", multiple=False):
    dialog = Gtk.FileChooserDialog(title, None, Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    dialog.set_default_response(Gtk.ResponseType.OK)
    dialog.set_select_multiple(multiple)
    response = dialog.run()
    result = None
    if response == Gtk.ResponseType.OK:
        result = dialog.get_filenames()
    dialog.destroy()
    return result

def save_file_chooser_dialog(title="Choose a file", pattern="*.csv"):
    dialog = Gtk.FileChooserDialog(title, None, Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                            Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
    dialog.set_default_response(Gtk.ResponseType.OK)
    dialog.set_current_name(pattern)
    response = dialog.run()
    result = None
    if response == Gtk.ResponseType.OK:
        result = dialog.get_filename()
    dialog.destroy()
    return result

def warning_dialog(text="", title="Warning", cancel=False):
    if cancel:
        dialog = Gtk.MessageDialog(type=Gtk.MessageType.QUESTION,
                                       buttons=Gtk.ButtonsType.OK_CANCEL,
                                       message_format=text,
                                       flags=Gtk.DialogFlags.MODAL)
    else:
        dialog = Gtk.MessageDialog(type=Gtk.MessageType.WARNING,
                                       buttons=Gtk.ButtonsType.OK,
                                       message_format=text,
                                       flags=Gtk.DialogFlags.MODAL)
    dialog.set_title(title)
    result = dialog.run()
    dialog.destroy()
    return result

def calendar_dialog(title="Calendar", date=None):
    dialog = Gtk.Dialog(title=title, flags=Gtk.DialogFlags.MODAL)
    dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK,
                       Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
    calendar = Gtk.Calendar()
    if date:
        try:
            year, month, day = date.split("-")
            calendar.select_month(int(month)-1, int(year))
            calendar.select_day(int(day))
        except:
            pass
    dialog.vbox.pack_start(calendar, True, True, 0)
    calendar.show()
    result = dialog.run()
    dialog.destroy()
    if result == Gtk.ResponseType.OK:
        date = calendar.get_date()
        return "%0.4d-%0.2d-%0.2d" % (date[0], date[1] + 1, date[2])
    elif result == Gtk.ResponseType.CANCEL:
        return None
