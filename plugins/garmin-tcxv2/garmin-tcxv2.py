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
from pytrainer.lib.xmlUtils import XMLParser
from pytrainer.gui.dialogs import fileChooserDialog, guiFlush

class garminTCXv2():
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
		selectedFiles = fileChooserDialog(title="Choose a TCX file (or files) to import", multiple=True).getFiles()
		guiFlush()
		importfiles = []
		if not selectedFiles: #Nothing selected
			return importfiles
		for filename in selectedFiles: #Multiple files
			if self.valid_input_file(filename): #TODO could consolidate tree generation here
				tree = etree.ElementTree(file=filename)
				#Possibly multiple entries in file
				activities = self.getActivities(tree)
				for activity in activities:
					if not self.inDatabase(activity):
						sport = self.getSport(activity)
						gpxfile = "%s/garmin-tcxv2-%d.gpx" % (self.tmpdir, len(importfiles))
						self.createGPXfile(gpxfile, activity)
						importfiles.append((gpxfile, sport))
					else:
						logging.debug("File:%s activity %d already in database. Skipping import." % (filename, activities.index(activity)) )
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
			xslfile = os.path.realpath(self.pytrainer_main.data_path)+ "/schemas/GarminTrainingCenterDatabase_v2.xsd"
			from pytrainer.lib.xmlValidation import xmlValidator
			validator = xmlValidator()
			return validator.validateXSL(filename, xslfile)

	def getActivities(self, tree):
		'''Function to return all activities in Garmin training center version 2 file
		'''
		root = tree.getroot()
		activities = root.findall(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Activity")
		return activities

	def inDatabase(self, activity):
		#comparing date and start time (sport may have been changed in DB after import)
		time = self.detailsFromTCX(activity)
		if self.pytrainer_main.ddbb.select("records","*","date_time_utc=\"%s\"" % (time)):
			return True
		else:
			return False

	def getSport(self, activity):
		#return sport from file or overide if present
		if self.sport:
			return self.sport
		#sportElement = activity.find(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Activity")
		try:
			sport = activity.get("Sport")
		except:
			sport = "import"
		return sport

	def detailsFromTCX(self, activity):
		timeElement = activity.find(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Id")
		if timeElement is None:
			return None
		else:
			return timeElement.text

	def createGPXfile(self, gpxfile, activity):
		""" Function to transform a Garmin Training Center v2 Track to a valid GPX+ file
		"""
		xslt_doc = etree.parse(self.data_path+"/translate.xsl")
		transform = etree.XSLT(xslt_doc)
		#xml_doc = etree.parse(filename)
		xml_doc = activity
		result_tree = transform(xml_doc)
		result_tree.write(gpxfile, xml_declaration=True, encoding='UTF-8')
