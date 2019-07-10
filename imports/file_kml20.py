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
import math
import datetime
from dateutil.tz import *
from io import BytesIO
from lxml import etree

class kml20():
	def __init__(self, parent = None, data_path = None):
		self.parent = parent
		self.pytrainer_main = parent.parent
		self.tmpdir = self.pytrainer_main.profile.tmpdir
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
				self.activities.append(xmldoc) # Assuming one activity per file
				#Valid file
				self.xmldoc = xmldoc
				self.startTime = datetime.datetime.now(tzlocal())
				inDatabase = False #cant really check, as dont have start time etc
				duration  = 0 #
				distance = self.getDistance(xmldoc)
				index = "%d:%d" % (0,0) 
				sport = "Running"
				self.activitiesSummary.append( (index,
												inDatabase, 
												self.startTime.strftime("%Y-%m-%dT%H:%M:%S%z"), 
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

	def getDistance(self, xmldoc):
		''' function to calculate distance from gps coordinates - code from gpx.py and of uncertain origins....
		'''
		total_dist = 0
		last_lat = last_lon = None
		coords = xmldoc.find(".//{http://earth.google.com/kml/2.0}coordinates")
		if coords is None:
			return total_dist
		else:
			logging.debug("Found %s coords" % len(coords))
			items = coords.text.strip().split()
			lat = lon = None
			for item in items:
				lon, lat, other = item.split(',')
				#Convert lat and lon from degrees to radians
				tmp_lat = float(lat)*0.01745329252  #0.01745329252 = number of radians in a degree
				tmp_lon = float(lon)*0.01745329252  #57.29577951 = 1/0.01745329252 or degrees per radian
				if last_lat is not None:
					try:
						#dist=math.acos(tempnum)*111.302*57.29577951
						dist=math.acos((math.sin(last_lat)*math.sin(tmp_lat))+(math.cos(last_lat)*math.cos(tmp_lat)*math.cos(tmp_lon-last_lon)))*111.302*57.29577951
					except Exception as e:
						print(e)
						dist=0
					total_dist += dist
				last_lat = tmp_lat
				last_lon = tmp_lon
		return round(total_dist, 2)

	def getGPXFile(self, ID, file_id):
		'''
			Generate GPX file based on activity ID
			Returns (sport, GPX filename)
		'''
		sport = None
		gpxFile = None
		#index = "%d:%d" % (self.activities.index((sport, activities)), activities.index(activity))
		sportID, activityID = ID.split(':')
		sportID = int(sportID)
		activityID = int(activityID)
		#activities = self.activities[sportID]
		activitiesCount = len(self.activities)
		if activitiesCount > 0 and activityID < activitiesCount:
			gpxFile = "%s/kml20-%s-%d.gpx" % (self.tmpdir, file_id, activityID)
			activity = self.activities[activityID]
			self.createGPXfile(gpxFile, activity)
		return sport, gpxFile

	def createGPXfile(self, gpxfile, activity):
		''' Function to transform a Garmin Training Center v2 Track to a valid GPX+ file
		'''
		tree = etree.parse(BytesIO(b'''<?xml version='1.0' encoding='ASCII'?>
							<gpx creator="pytrainer http://sourceforge.net/projects/pytrainer" 
								version="1.1" 
								xmlns="http://www.topografix.com/GPX/1/1" 
								xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" >
							</gpx>'''))
							
		root = tree.getroot()
		
		metadata = etree.SubElement(root, "metadata")
		name = etree.SubElement(metadata, "name")
		name.text = "NeedsaName" #TODO
		link = etree.SubElement(metadata, "link", href="http://sourceforge.net/projects/pytrainer")
		time = etree.SubElement(metadata, "time")
		time.text = self.startTime.strftime("%Y-%m-%dT%H:%M:%S%z")
		trk = etree.SubElement(root, "trk")
		trkseg = etree.SubElement(trk, "trkseg")
		#for trkpt in file
		coords = activity.find(".//{http://earth.google.com/kml/2.0}coordinates")
		if coords is None:
			pass
		else:
			items = coords.text.strip().split()
			lat = lon = None
			for item in items:
				lon, lat, other = item.split(',')
				trkpt = etree.SubElement(trkseg, "trkpt", lat=lat, lon=lon)
				ele = etree.SubElement(trkpt, "ele")
				ele.text = "0" #TODO
				#trkpt_time = etree.SubElement(trkpt, "time")
				#trkpt_time.text = "2010-03-02T04:52:35Z" #TODO
		
		#print(etree.tostring(tree, pretty_print=True))

		tree.write(gpxfile, method="xml", pretty_print=True, xml_declaration=True)
