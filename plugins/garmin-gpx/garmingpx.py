#!/usr/bin/env python

#Copyright (C) 

#Based on plugin by Kevin Dwyer kevin@pheared.net

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

import logging
from gui.dialogs import fileChooserDialog, guiFlush
import xml.etree.cElementTree

class garmingpx():
	""" Plugin to import from a GPX file or files
		Expects only one activity in each file 
		Checks to see if any entries are in the database with the same start time
	"""
	def __init__(self, parent = None):
		self.parent = parent
		self.tmpdir = self.parent.conf.getValue("tmpdir")

	def run(self):
		selectedFiles = fileChooserDialog(title="Choose a GPX file (or files) to import", multiple=True).getFiles()
		guiFlush()
		importFiles = []
		for filename in selectedFiles:
			if not self.inDatabase(filename):
				importFiles.append(filename)
			else:
				print "%s already in database. Skipping import." % (filename,) 
				logging.debug("%s already in database. Skipping import." % (filename,) )
		return importFiles

	def inDatabase(self, filename):
		#comparing date and start time (sport may have been changed in DB after import)
		time = self.detailsFromGPX(filename)
		if self.parent.parent.ddbb.select("records","*","date_time_utc=\"%s\"" % (time)):
			return True
		else:
			return False

	def detailsFromGPX(self, filename):
		tree = xml.etree.cElementTree.ElementTree(file=filename)
		root = tree.getroot()
		timeElement = root.find(".//{http://www.topografix.com/GPX/1/1}time")
		if timeElement is None:
			return None
		else:
			return timeElement.text

		
