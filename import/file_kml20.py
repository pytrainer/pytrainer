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
import datetime
from lxml import etree

from pytrainer.lib.xmlUtils import XMLParser
from pytrainer.lib.system import checkConf
from pytrainer.lib.date import Date
#from pytrainer.gui.dialogs import fileChooserDialog, guiFlush

class kml20():
	def __init__(self, parent = None, data_path = None):
		self.parent = parent
		self.conf = checkConf()
		self.tmpdir = self.conf.getValue("tmpdir")
		self.main_data_path = data_path
		self.data_path = os.path.dirname(__file__)
		self.xmldoc = None
		self.activitiesSummary = []
		self.activities = []
		#self.sportsList = ("Running", "Biking", "Other", "MultiSport")

	def getXmldoc(self):
		''' Function to return parsed xmlfile '''
		return self.xmldoc

	def getFileType(self):
		return _("Geodistance kml version 2.0 file")

	def getActivitiesSummary(self):
		return self.activitiesSummary

	def testFile(self, filename):
		logging.debug('>>')
		logging.debug("Testing " + filename)
		try:
			#parse filename as xml
			xmldoc = etree.parse(filename)
			#Parse XML schema
			xmlschema_doc = etree.parse(self.main_data_path+"schemas/kml20-geodistance.xsd")
			xmlschema = etree.XMLSchema(xmlschema_doc)
			if (xmlschema.validate(xmldoc)):
				#Valid file
				self.xmldoc = xmldoc
				startTime = datetime.datetime.now()
				inDatabase = False #cant really check, as dont have start time etc
				duration  = 0 #
				distance = ""
				index = "%d:%d" % (0,0) 
				sport = "Running"
				self.activitiesSummary.append( (index,
												inDatabase, 
												startTime.strftime("%Y-%m-%dT%H:%M:%S"), 
												distance, 
												str(duration), 
												sport,
												) )
				#print self.activitiesSummary
				return True
		except:
			#Not valid file
			return False 
		return False

	def getDateTime(self, time_):
		return Date().getDateTime(time_)

	def getGPXFile(self, ID, file_id):
		'''
			Generate GPX file based on activity ID
			Returns (sport, GPX filename)
		'''
		'''sport = None
		gpxFile = None
		#index = "%d:%d" % (self.activities.index((sport, activities)), activities.index(activity))
		sportID, activityID = ID.split(':')
		sportID = int(sportID)
		activityID = int(activityID)
		sport, activities = self.activities[sportID]
		activitiesCount = len(self.activities)
		if activitiesCount > 0 and activityID < activitiesCount:
			gpxFile = "%s/kml20-%s-%d.gpx" % (self.tmpdir, file_id, activityID)
			activity = activities[activityID]
			self.createGPXfile(gpxFile, activity)
		return sport, gpxFile'''

	def createGPXfile(self, gpxfile, activity):
		''' Function to transform a Garmin Training Center v2 Track to a valid GPX+ file
		'''
		'''xslt_doc = etree.parse(self.data_path+"/translate_garmintcxv1.xsl")
		transform = etree.XSLT(xslt_doc)
		#xml_doc = etree.parse(filename)
		xml_doc = activity
		result_tree = transform(xml_doc)
		result_tree.write(gpxfile, xml_declaration=True)'''

