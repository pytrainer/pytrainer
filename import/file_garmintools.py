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
import StringIO
from lxml import etree
from pytrainer.lib.date import Date

#from pytrainer.lib.xmlUtils import XMLParser
#from pytrainer.gui.dialogs import fileChooserDialog, guiFlush
from pytrainer.lib.system import checkConf

class garmintools():
	def __init__(self, parent = None, data_path = None):
		self.parent = parent
		self.conf = checkConf()
		self.tmpdir = self.conf.getValue("tmpdir")
		self.main_data_path = data_path
		self.data_path = os.path.dirname(__file__)
		self.xmldoc = None
		self.activitiesSummary = []

	def getXmldoc(self):
		''' Function to return parsed xmlfile '''
		return self.xmldoc

	def getFileType(self):
		return _("Garmin tools dump file")

	def getActivitiesSummary(self):
		return self.activitiesSummary

	def testFile(self, filename):
		logging.debug('>>')
		logging.debug("Testing " + filename)
		#Check if file is a garmintools dump
		try:
			with open(filename, 'r') as f:
				xmlString = f.read()
			#add a root element to make correct xml
			fileString = StringIO.StringIO("<root>"+xmlString+"</root>")
			#parse string as xml
			xmldoc = etree.parse(fileString)
			#Parse XML schema
			xmlschema_doc = etree.parse(self.main_data_path+"schemas/garmintools.xsd")
			xmlschema = etree.XMLSchema(xmlschema_doc)
			if (xmlschema.validate(xmldoc)):
				#Valid garmintools file
				self.xmldoc = xmldoc
				startTime = self.getDateTime(self.startTimeFromFile(xmldoc))
				indatabase = self.inDatabase(xmldoc, startTime)
				sport = self.getSport(xmldoc)
				distance, duration  = self.getDetails(xmldoc, startTime)
				distance = distance / 1000.0
				self.activitiesSummary.append( (0,
												indatabase, 
												startTime[1].strftime("%Y-%m-%dT%H:%M:%S"), 
												"%0.2f" % distance , 
												str(duration), 
												sport,
												) )
				return True
		except:
			#Not garmintools dump file
			return False
		return False
	
	def getDateTime(self, time_):
		return Date().getDateTime(time_)

	def inDatabase(self, tree, startTime):
		#comparing date and start time (sport may have been changed in DB after import)
		time = startTime
		if time is None:
			return False
		time = time[0].strftime("%Y-%m-%dT%H:%M:%SZ")
		if self.parent.parent.ddbb.select("records","*","date_time_utc=\"%s\"" % (time)):
			return True
		else:
			return False

	def getDetails(self, tree, startTime):
		root = tree.getroot()
		points = root.findall(".//point")
		while True:
			lastPoint = points[-1]
			try:
				distance = lastPoint.get("distance")
				if distance is None:
					points = points[:-1]
					continue
				time = lastPoint.get("time")
				break
			except:
				points = points[:-1]
				continue
		return float(distance), self.getDateTime(time)[0]-startTime[0]

	def getSport(self, tree):
		#return sport from file
		root = tree.getroot()
		sportElement = root.find(".//run")
		try:
			sport = sportElement.get("sport")
			sport = sport.capitalize()
		except:
			sport = "import"
		return sport

	def startTimeFromFile(self, tree):
		root = tree.getroot()
		#Find first point
		pointElement = root.find(".//point")
		if pointElement is not None:
			#Try to get time from point
			time = pointElement.get("time")
			print "#TODO first time is different from time used by gpsbabel and has locale embedded: " + time
			return time
		return None

	def getGPXFile(self, ID, file_id):
		"""
			Generate GPX file based on activity ID

			Returns (sport, GPX filename)
		"""
		sport = None
		gpxFile = None
		if ID == "0": #Only one activity in file
			gpxFile = "%s/garmintools-%s-%s.gpx" % (self.tmpdir, file_id, ID)
			sport = self.getSport(self.xmldoc)
			self.createGPXfile(gpxFile, self.xmldoc)
		return sport, gpxFile

	def createGPXfile(self, gpxfile, tree):
		""" Function to transform a Garmintools dump file to a valid GPX+ file
		"""
		xslt_doc = etree.parse(self.data_path+"/translate_garmintools.xsl")
		transform = etree.XSLT(xslt_doc)
		result_tree = transform(tree)
		result_tree.write(gpxfile, xml_declaration=True)

