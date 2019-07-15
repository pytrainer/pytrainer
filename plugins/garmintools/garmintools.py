# -*- coding: utf-8 -*-

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

# Added to support python installations older than 2.6
from __future__ import with_statement

import logging
import os
from io import BytesIO
from lxml import etree

from pytrainer.lib.xmlUtils import XMLParser
from pytrainer.gui.dialogs import fileChooserDialog, guiFlush
from pytrainer.core.activity import Activity
from sqlalchemy.orm import exc

class garmintools():
	def __init__(self, parent = None, validate=False):
		self.parent = parent
		self.pytrainer_main = parent.pytrainer_main
		self.tmpdir = self.pytrainer_main.profile.tmpdir
		self.data_path = os.path.dirname(__file__)
		self.validate = validate
		self.sport = self.getConfValue("Force_sport_to")

	def getConfValue(self, confVar):
		info = XMLParser(self.data_path+"/conf.xml")
		code = info.getValue("pytrainer-plugin","plugincode")
		plugindir = self.pytrainer_main.profile.plugindir
		if not os.path.isfile(plugindir+"/"+code+"/conf.xml"):
			value = None
		else:
			info = XMLParser(plugindir+"/"+code+"/conf.xml")
			value = info.getValue("pytrainer-plugin",confVar)
		return value

	def run(self):
		logging.debug(">>")
		# able to select multiple files....
		selectedFiles = fileChooserDialog(title="Choose a garmintools dump file (or files) to import", multiple=True).getFiles()
		guiFlush()
		importfiles = []
		if not selectedFiles: #Nothing selected
			return importfiles
		for filename in selectedFiles:
			if self.valid_input_file(filename):
				#Garmin dump files are not valid xml - need to load into a xmltree
				#read file into string
				with open(filename, 'r') as f:
					xmlString = f.read()
				fileString = BytesIO(b"<root>" + xmlString + b"</root>")
				#parse string as xml
				tree = etree.parse(fileString)
				if not self.inDatabase(tree):
					sport = self.getSport(tree)
					gpxfile = "%s/garmintools-%d.gpx" % (self.tmpdir, len(importfiles))
					self.createGPXfile(gpxfile, tree)
					importfiles.append((gpxfile, sport))
				else:
					logging.debug("%s already in database. Skipping import." % (filename,) )
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
			print("Cannot validate garmintools dump files yet")
			logging.debug("Cannot validate garmintools dump files yet")
			return True
			'''xslfile = os.path.realpath(self.parent.parent.data_path)+ "/schemas/GarminTrainingCenterDatabase_v2.xsd"
			from lib.xmlValidation import xmlValidator
			validator = xmlValidator()
			return validator.validateXSL(filename, xslfile)'''

	def inDatabase(self, tree):
		#comparing date and start time (sport may have been changed in DB after import)
		time = self.detailsFromFile(tree)
		try:
			self.pytrainer_main.ddbb.session.query(Activity).filter(Activity.date_time_utc == time).one()
			return True
		except exc.NoResultFound:
			return False

	def getSport(self, tree):
		#return sport from file or overide if present
		if self.sport:
			return self.sport
		root = tree.getroot()
		sportElement = root.find(".//run")
		try:
			sport = sportElement.get("sport")
			sport = sport.capitalize()
		except:
			sport = "import"
		return sport

	def detailsFromFile(self, tree):
		root = tree.getroot()
		#Find first point
		pointElement = root.find(".//point")
		if pointElement is not None:
			#Try to get time from point
			time = pointElement.get("time")
			print("#TODO first time is different from time used by gpsbabel and has locale embedded: " + time)
			return time
		return None

	def createGPXfile(self, gpxfile, tree):
		""" Function to transform a Garmintools dump file to a valid GPX+ file
		"""
		xslt_doc = etree.parse(self.data_path+"/translate.xsl")
		transform = etree.XSLT(xslt_doc)
		result_tree = transform(tree)
		result_tree.write(gpxfile, xml_declaration=True, encoding='UTF-8')

