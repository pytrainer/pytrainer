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
import dateutil.parser
from dateutil.tz import * # for tzutc()

from pytrainer.lib.xmlUtils import XMLParser
from pytrainer.lib.system import checkConf
#from pytrainer.gui.dialogs import fileChooserDialog, guiFlush

class garmintcxv2():
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
		return _("Garmin training center database file version 2")

	def getActivitiesSummary(self):
		return self.activitiesSummary

	def getDetails(self, activity, startTime):
		points = activity.findall(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint")
		while True:
			lastPoint = points[-1]
			try:
				distance = lastPoint.find(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}DistanceMeters")
				if distance is None:
					points = points[:-1]
					continue
				time = lastPoint.find(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Time")
				distance = distance.text
				time = time.text
				break
			except:
				#Try again without the last point (i.e work from end until find time and distance)
				points = points[:-1]
				continue
		return float(distance), self.getDateTime(time)[0]-startTime[0]

	def testFile(self, filename):
		logging.debug('>>')
		logging.debug("Testing " + filename)
		try:
			#parse filename as xml
			xmldoc = etree.parse(filename)
			#Parse XML schema
			xmlschema_doc = etree.parse(self.main_data_path+"schemas/GarminTrainingCenterDatabase_v2.xsd")
			xmlschema = etree.XMLSchema(xmlschema_doc)
			if (xmlschema.validate(xmldoc)):
				#Valid file
				self.xmldoc = xmldoc
				#Possibly multiple entries in file
				activities = self.getActivities(xmldoc)
				for activity in activities:
					startTime = self.getDateTime(self.getStartTimeFromActivity(activity))
					inDatabase = self.inDatabase(activity, startTime)
					sport = self.getSport(activity)

				 	distance, duration  = self.getDetails(activity, startTime)
					distance = distance / 1000.0
					self.activitiesSummary.append( (activities.index(activity),
													inDatabase, 
													startTime[1].strftime("%Y-%m-%dT%H:%M:%S"), 
													"%0.2f" % distance , 
													str(duration), 
													sport,
													) )
				#print self.activitiesSummary
				return True
		except:
			#Not valid file
			return False 
		return False

	def getActivities(self, tree):
		'''Function to return all activities in Garmin training center version 2 file
		'''
		root = tree.getroot()
		activities = root.findall(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Activity")
		return activities

	def inDatabase(self, activity, startTime):
		#comparing date and start time (sport may have been changed in DB after import)
		time = startTime
		if time is None:
			return False
		time = time[0].strftime("%Y-%m-%dT%H:%M:%SZ")
		if self.parent.parent.ddbb.select("records","*","date_time_utc=\"%s\"" % (time)):
			return True
		else:
			return False

	def getSport(self, activity):
		#return sport from activity
		#sportElement = activity.find(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Activity")
		try:
			sport = activity.get("Sport")
		except:
			sport = "import"
		return sport

	def getStartTimeFromActivity(self, activity):
		timeElement = activity.find(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Id")
		if timeElement is None:
			return None
		else:
			return timeElement.text

	def getDateTime(self, time_):
		# Time can be in multiple formats
		# - zulu 			2009-12-15T09:00Z
		# - local ISO8601	2009-12-15T10:00+01:00
		if time_ is None or time_ == "":
			return (None, None)
		dateTime = dateutil.parser.parse(time_)
		timezone = dateTime.tzname()
		if timezone == 'UTC': #got a zulu time
			local_dateTime = dateTime.astimezone(tzlocal()) #datetime with localtime offset (from OS)
		else:
			local_dateTime = dateTime #use datetime as supplied
		utc_dateTime = dateTime.astimezone(tzutc()) #datetime with 00:00 offset
		#print utc_dateTime, local_dateTime
		return (utc_dateTime,local_dateTime)

	'''def createGPXfile(self, gpxfile, activity):
		""" Function to transform a Garmin Training Center v2 Track to a valid GPX+ file
		"""
		xslt_doc = etree.parse(self.data_path+"/translate.xsl")
		transform = etree.XSLT(xslt_doc)
		#xml_doc = etree.parse(filename)
		xml_doc = activity
		result_tree = transform(xml_doc)
		result_tree.write(gpxfile, xml_declaration=True)'''

