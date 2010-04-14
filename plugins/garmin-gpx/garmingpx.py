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
import os
import shutil
import xml.etree.cElementTree

from pytrainer.gui.dialogs import fileChooserDialog, guiFlush
from pytrainer.lib.xmlUtils import XMLParser

class garmingpx():
	""" Plugin to import from a GPX file or files
		Expects only one activity in each file 
		Checks to see if any entries are in the database with the same start time
	"""
	def __init__(self, parent = None, validate=False):
		self.parent = parent
		self.tmpdir = self.parent.profile.tmpdir
		self.validate = validate
		self.data_path = os.path.dirname(__file__)
		self.sport = self.getConfValue("Force_sport_to")

	def getConfValue(self, confVar):
		info = XMLParser(self.data_path+"/conf.xml")
		code = info.getValue("pytrainer-plugin","plugincode")
		plugindir = self.parent.conf.getValue("plugindir")
		if not os.path.isfile(plugindir+"/"+code+"/conf.xml"):
			value = None
		else:
			info = XMLParser(plugindir+"/"+code+"/conf.xml")
			value = info.getValue("pytrainer-plugin",confVar)
		return value

	def run(self):
		logging.debug(">>")
		selectedFiles = fileChooserDialog(title="Choose a GPX file (or files) to import", multiple=True).getFiles()
		guiFlush()
		importfiles = []
		if not selectedFiles:
			return importfiles
		for filename in selectedFiles:
			if self.valid_input_file(filename):
				if not self.inDatabase(filename):
					sport = self.getSport(filename)
					gpxfile = "%s/garmin-gpx-%d.gpx" % (self.tmpdir, len(importfiles))	
					shutil.copy(filename, gpxfile)
					importfiles.append((gpxfile, sport))
				else:
					logging.debug("%s already in database. Skipping import." % (filename) )
			else:
				logging.info("File %s failed validation" % (filename))
		logging.debug("<<")
		return importfiles

	def valid_input_file(self, filename):
		""" Function to validate input file if requested"""
		if not self.validate:  #not asked to validate
			logging.debug("Not validating %s" % (filename) )
			return True
		else:
			#To validate GPX as used for pytrainer must test against both Topograpfix and Cluetrust
			topografixXSLfile = os.path.realpath(self.parent.parent.data_path)+ "/schemas/Topografix_gpx11.xsd"
			cluetrustXSLfile = os.path.realpath(self.parent.parent.data_path)+ "/schemas/Cluetrust_gpxdata10.xsd"
			from lib.xmlValidation import xmlValidator
			validator = xmlValidator()
			return validator.validateXSL(filename, topografixXSLfile) and validator.validateXSL(filename, cluetrustXSLfile)

	def inDatabase(self, filename):
		""" Function to determine if a given file has already been imported into the database
		    only compares date and start time (sport may have been changed in DB after import)
			only valid for GPX files with a single activity 
		"""
		time = self.detailsFromGPX(filename)
		if self.parent.parent.ddbb.select("records","*","date_time_utc=\"%s\"" % (time)):
			return True
		else:
			return False

	def getSport(self, filename):
		#return sport from overide if present or default to "import"
		if self.sport:
			return self.sport
		sport = "import"
		return sport

	def detailsFromGPX(self, filename):
		""" Function to return the first time element from a GPX 1.1 file """
		tree = xml.etree.cElementTree.ElementTree(file=filename)
		root = tree.getroot()
		timeElement = root.find(".//{http://www.topografix.com/GPX/1/1}time")
		if timeElement is None:
			return None
		else:
			return timeElement.text

		
