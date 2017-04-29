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
import pygtk
pygtk.require('2.0')
import gtk
import logging

class fileChooserDialog():
    def __init__(self, title = "Choose a file", multiple = False):
        logging.warning("Deprecated fileChooserDialog class called")
        self.inputfiles = open_file_chooser_dialog(title=title, multiple=multiple)

    def getFiles(self):
        return self.inputfiles

class guiFlush():
    def __init__(self):
        dialog = gtk.Dialog(title=None, parent=None, flags=0, buttons=None)
        dialog.show()
        dialog.destroy()

def open_file_chooser_dialog(title="Choose a file", multiple=False):
    dialog = gtk.FileChooserDialog(title, None, gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    dialog.set_default_response(gtk.RESPONSE_OK)
    dialog.set_select_multiple(multiple)
    response = dialog.run()
    result = None
    if response == gtk.RESPONSE_OK:
        result = dialog.get_filenames()
    dialog.destroy()
    return result

def save_file_chooser_dialog(title="Choose a file", pattern="*.csv"):
    dialog = gtk.FileChooserDialog(title, None, gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                            gtk.STOCK_SAVE, gtk.RESPONSE_OK))
    dialog.set_default_response(gtk.RESPONSE_OK)
    dialog.set_current_name(pattern)
    response = dialog.run()
    result = None
    if response == gtk.RESPONSE_OK:
        result = dialog.get_filename()
    dialog.destroy()
    return result

def warning_dialog(text="", title="Warning", cancel=False):
    if cancel:
        dialog = gtk.MessageDialog(type=gtk.MESSAGE_QUESTION,
                                       buttons=gtk.BUTTONS_OK_CANCEL,
                                       message_format=text,
                                       flags=gtk.DIALOG_MODAL)
    else:
        dialog = gtk.MessageDialog(type=gtk.MESSAGE_WARNING,
                                       buttons=gtk.BUTTONS_OK,
                                       message_format=text,
                                       flags=gtk.DIALOG_MODAL)
    dialog.set_title(title)
    result = dialog.run()
    dialog.destroy()
    return result
