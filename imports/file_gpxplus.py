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

import logging
import os
import traceback
from lxml import etree
from pytrainer.lib.date import getDateTime
from pytrainer.core.activity import Activity
from sqlalchemy.orm import exc

class gpxplus():
	def __init__(self, parent = None, data_path = None):
		self.parent = parent
		self.pytrainer_main = parent.parent
		self.tmpdir = self.pytrainer_main.profile.tmpdir
		self.main_data_path = data_path
		self.data_path = os.path.dirname(__file__)
		self.xmldoc = None
		self.activitiesSummary = []

	def getXmldoc(self):
		''' Function to return parsed xmlfile '''
		return self.xmldoc

	def getFileType(self):
		return _("GPS eXchange file")

	def getActivitiesSummary(self):
		return self.activitiesSummary

	def testFile(self, filename):
		logging.debug('>>')
		logging.debug("Testing " + filename)
		#Check if file is a GPX
		try:
			#parse as xml
			xmldoc = etree.parse(filename)
			#Parse XML schema
			xmlschema_doc = etree.parse(self.main_data_path+"schemas/Topografix_gpx11.xsd")
			xmlschema = etree.XMLSchema(xmlschema_doc)
			if (xmlschema.validate(xmldoc)):
				#Valid gpx file
				self.xmldoc = xmldoc
				startTime = getDateTime(self.startTimeFromFile(xmldoc))
				indatabase = self.inDatabase(xmldoc, startTime)
				sport = self.getSport(xmldoc)
				duration  = self.getDetails(xmldoc, startTime)
				distance = ""
				self.activitiesSummary.append( (0,
												indatabase,
												startTime[1].strftime("%Y-%m-%dT%H:%M:%S"),
												distance ,
												str(duration),
												sport,
												) )
				return True
		except:
			#Not gpx file
			logging.debug("Traceback: %s" % traceback.format_exc())
			return False
		return False

	def inDatabase(self, tree, startTime):
		#comparing date and start time (sport may have been changed in DB after import)
		time = startTime
		if time is None:
			return False
		time = time[0].strftime("%Y-%m-%dT%H:%M:%SZ")
		try:
			self.parent.parent.ddbb.session.query(Activity).filter(Activity.date_time_utc == time).one()
			return True
		except exc.NoResultFound:
			return False

	def getDetails(self, tree, startTime):
		root = tree.getroot()
		#Get all times from file
		times = root.findall(".//{http://www.topografix.com/GPX/1/1}time")
		time = times[-1].text
		return getDateTime(time)[0]-startTime[0]

	def getSport(self, tree):
		#No sport in GPX file
		return None

	def startTimeFromFile(self, tree):
		""" Function to return the first time element from a GPX 1.1 file (skipping not mandatory metadata section) """
		root = tree.getroot()
		timeElement = root.xpath(".//g:time[not(parent::g:metadata)]", namespaces={'g':'http://www.topografix.com/GPX/1/1'})[0]
		if timeElement is not None:
			return timeElement.text
		return None

	def getGPXFile(self, ID, file_id):
		"""
			Generate GPX file based on activity ID

			Returns (sport, GPX filename)
		"""
		sport = None
		gpxFile = None
		if ID == "0": #Only one activity in file
			gpxFile = "%s/gpx-%s-%s.gpx" % (self.tmpdir, file_id, ID)
			sport = self.getSport(self.xmldoc)
			self.createGPXfile(gpxFile, self.xmldoc)
		return sport, gpxFile

	def createGPXfile(self, gpxfile, tree):
		tree.write(gpxfile, xml_declaration=True, encoding='UTF-8')

