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

class fileChooserDialog():
	def __init__(self, title = "Choose a file", multiple = False):
		dialog = gtk.FileChooserDialog(title, None, gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)) 
		dialog.set_default_response(gtk.RESPONSE_OK)
		dialog.set_select_multiple(multiple)
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			self.inputfiles = dialog.get_filenames()
		elif response == gtk.RESPONSE_CANCEL:
			self.inputfiles = None
		dialog.destroy()

	def getFiles(self):
		return self.inputfiles

class guiFlush():
	def __init__(self):
		dialog = gtk.Dialog(title=None, parent=None, flags=0, buttons=None)
		dialog.show()
		dialog.destroy()




