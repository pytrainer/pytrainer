# -*- coding: iso-8859-1 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net
# vud1@grupoikusnet.com
# Jakinbidea & Grupo Ikusnet Developer
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

import os
import string
import logging
import xml.dom
from xml.dom import minidom, Node, getDOMImplementation
import xml.etree.cElementTree

# use of namespaces is mandatory if defined
mainNSGarmin = string.Template("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v1}$tag")
timeTag = mainNSGarmin.substitute(tag="time")
trackTag = mainNSGarmin.substitute(tag="trk")
trackPointTag = mainNSGarmin.substitute(tag="trkpt")

class XMLParser:
	def __init__(self,filename = None):
		self.filename = filename
		self._load()

	def _load(self):
		try: 
			self.xmldoc = xml.dom.minidom.parse(self.filename) 
		except:
			self.xmldoc = None
			
	def setOptions(self,list_item, version):
		list_item.append(("version",version))
		self.createXMLFile(self,"pytraining",list_item)

	def getOptions(self):
		self._load()
		root = self.xmldoc.getElementsByTagName("pytraining")[0]
		list_options = {}
		list_keys = root.attributes.keys()
		for i in list_keys:
			value = self.getValue("pytraining",i)
			list_options[i] = value
		return list_options	
	
	def getOption(self,option):
		print "this function is obsolete, use getValue instead"
		return self.getValue("pytraining",option)
		
	def setVersion(self,version):
		self.setValue("pytraining","version",version)

	def setValue(self,tagname,variable,value):
		root = self.xmldoc.getElementsByTagName(tagname)[0]
		if root.attributes.has_key(variable):
			root.attributes[variable]._set_value(value)
		else:
			root.setAttribute(variable,value)
		content = self.xmldoc.toprettyxml()
		self._saveFile(content)

	def getValue(self,tagname,variable):
		self._load()
		root = self.xmldoc.getElementsByTagName(tagname)[0]
		value = root.attributes[variable].value
		return value
	
	def getAllValues(self,tagname):	
		self._load()
		root = self.xmldoc.getElementsByTagName(tagname)
		retorno = []
		for i in root:
			retorno.append((i.attributes["variable"].value, i.attributes["value"].value))
		return retorno
	
	def createXMLFile(self,tag,list_options):
		impl = getDOMImplementation()
		self.xmldoc = impl.createDocument(None, tag, None)
		top_element = self.xmldoc.documentElement
		#top_element.appendChild(text)
		for option in list_options:
			var = option[0]
			value = option[1]
			attr = self.xmldoc.createAttribute(var)
			top_element.setAttributeNode(attr)
			top_element.attributes[var]._set_value(value)
		xmlcontent = self.xmldoc.toprettyxml()
		self._saveFile(xmlcontent)	

	def _saveFile(self,xmlcontent):
		out = open(self.filename, 'w')
		out.write(xmlcontent)
		out.close()

	def shortFromGPS(self, gtrnctrFile, getSport=True):
		"""23.03.2008 - dgranda
		Retrieves sport, date and start time from each entry coming from GPS
		args:
			gtrnctrFile: file with data from GPS file (garmin format)
			getSport: indicates if sport info should be added
		returns: list with dictionaries (just a list in case of sport is not retrieved) SPORT|DATE_STARTTIME"""
		logging.debug('>>')
		listTracksGPS = []
		# http://gnosis.cx/publish/programming/parser-benchmarks.png
		# Using ElementTree -> http://effbot.org/zone/element-index.htm
		# cElementTree -> http://mike.hostetlerhome.com/present_files/pyxml.html
		logging.debug('parsing '+gtrnctrFile)
		if getSport is True:
			logging.debug('Retrieving sport info')
		else:
			logging.debug('Discarding sport info')
		listTracksGPS = []
		tree = xml.etree.cElementTree.parse(gtrnctrFile).getroot()
		history = tree.findall(".//History")
		for sport in history:
			#print "Element: "+sport.tag
			if sport.getchildren():
				for child in sport:
					#print "\tSport found: "+child.tag
					if child.getchildren():
						for entry in child:
							logging.debug("Entry found: "+entry.tag)
							tracks = entry.findall(".//Track")
							num_tracks = len(tracks)
							#print 'Tracks found: '+str(num_tracks)
							if num_tracks>0:
								for track in tracks:
									# we are looking for date and time for the first trackpoint
									date_time = track.findtext(".//Time") #returns first instance found
									track_sport = entry.tag
									logging.info('Found: '+track_sport+' | '+date_time)
									if getSport is True:
										listTracksGPS.append((track_sport,date_time))
									else:
										listTracksGPS.append(date_time)
					else:
						logging.debug("No entry found for "+child.tag)
		logging.debug('Retrieved info: '+str(listTracksGPS))
		logging.debug('<<')
		return listTracksGPS
		
		
	def getTrackFromDates(self, source_file , entry , isGpx):
		"""23.03.2008 - dgranda
		Retrieves track given sport, date and start time
		args:
			- source_file: absolute path to source file
			- entry: dictionary with SPORT|DATE_START_TIME
			- isGpx: 1 if source file is GPX, 0 if garmin format
		returns: path to selected entry file"""
		logging.debug('>>')
		selectedEntry = ""
		# 23.03.2008 Only source from garmin files are supported right now (isGpx = 0)
		# this is intended to work in the future with variables instead of hardcoded field names
		#dom = xml.dom.minidom.parse(source_file)
		trks = self.xmldoc.getElementsByTagName("Track")
		for trk in trks:
			trkpoints = trk.getElementsByTagName("Trackpoint")
			# we just need to check first one's date
			date_time = trkpoints[0].getElementsByTagName("Time")[0].firstChild.data
			if date_time == entry[1]:
				#this is the track we are looking for
				selectedEntry = "/tmp/track"+date_time
				logging.debug('Writing selected track to '+selectedEntry)
				f = open(selectedEntry,'w')
				f.write(trk.toxml())
				f.close()
		logging.debug('<<')
		return selectedEntry
