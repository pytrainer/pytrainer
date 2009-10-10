# -*- coding: iso-8859-1 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net
# Modified by dgranda

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
from lxml import etree

from gui.dialogs import fileChooserDialog, guiFlush

class garminTCXv2():
	def __init__(self, parent = None, validate=False):
		self.parent = parent
		self.tmpdir = self.parent.conf.getValue("tmpdir")
		self.data_path = os.path.dirname(__file__)
		self.validate = validate

	def run(self):
		logging.debug(">>")
		# able to select multiple files....
		selectedFiles = fileChooserDialog(title="Choose a TCX file (or files) to import", multiple=True).getFiles()
		guiFlush()
		importfiles = []
		if not selectedFiles: #Nothing selected
			return importfiles
		for filename in selectedFiles:
			if self.valid_input_file(filename):
				if not self.inDatabase(filename):
					gpxfile = "%s/garmin-tcxv2-%d.gpx" % (self.tmpdir, len(importfiles))					
					self.createGPXfile(gpxfile, filename)
					importfiles.append(gpxfile)					
				else:
					logging.debug("%s already in database. Skipping import." % (filename,) )
			else:
				logging.debug("Invalid input file %s" % (filename))
		logging.debug("<<")
		return importfiles

	def valid_input_file(self, filename):
		""" Function to validate input file if requested"""
		if not self.validate:
			#not asked to validate
			return True
		else:
			xslfile = os.path.realpath(self.parent.parent.data_path)+ "/schemas/GarminTrainingCenterDatabase_v2.xsd"
			from lib.xmlValidation import xmlValidator
			validator = xmlValidator()
			return validator.validateXSL(filename, xslfile)

	def inDatabase(self, filename):
		#comparing date and start time (sport may have been changed in DB after import)
		time = self.detailsFromTCX(filename)
		if self.parent.parent.ddbb.select("records","*","date_time_utc=\"%s\"" % (time)):
			return True
		else:
			return False

	def detailsFromTCX(self, filename):
		tree = etree.ElementTree(file=filename)
		root = tree.getroot()
		timeElement = root.find(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Id")
		if timeElement is None:
			return None
		else:
			return timeElement.text

	def createGPXfile(self, gpxfile, filename):
		""" Function to transform a Garmin Training Center v2 Track to a valid GPX+ file
		"""
		xslt_doc = etree.parse(self.data_path+"/translate.xsl")
		transform = etree.XSLT(xslt_doc)
		xml_doc = etree.parse(filename)
		result_tree = transform(xml_doc)
		result_tree.write(gpxfile)

