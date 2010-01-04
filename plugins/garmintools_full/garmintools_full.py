#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net

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
import sys
import logging
import fnmatch
import commands
import StringIO
from lxml import etree
from pytrainer.lib.xmlUtils import XMLParser
import dateutil.parser
from datetime import date, timedelta, datetime
from dateutil.tz import * # for tzutc()
import traceback

class garmintools_full():
	""" Plugin to import from a Garmin device using gpsbabel
		Checks each activity to see if any entries are in the database with the same start time
		Creates GPX files for each activity not in the database

		Note: using lxml see http://codespeak.net/lxml
	"""
	def __init__(self, parent = None, validate=False):
		self.parent = parent
		self.confdir = self.parent.conf.getValue("confdir")
		self.tmpdir = self.parent.conf.getValue("tmpdir")
		# Tell garmintools where to save retrieved data from GPS device
		os.environ['GARMIN_SAVE_RUNS']=self.tmpdir
		self.data_path = os.path.dirname(__file__)
		self.validate = validate
		self.sport = self.getConfValue("Force_sport_to")
		self.deltaDays = self.getConfValue("Not_older_days")
		if self.deltaDays is None:
			self.deltaDays = 0
		#so far hardcoded to False - dg 20100104
		#self.legacyComp = self.getConfValue("Legacy_comparison")
		self.legacyComp = False

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
		importFiles = []
		if self.checkLoadedModule():
			numError = self.getDeviceInfo()
			if numError >= 0:
				# Create a compressed copy of current user directory
				try: 
					self.createUserdirBackup()
				except:
					logging.error('Not able to make a copy of current user directory. Printing traceback and exiting')
					traceback.print_exc()
					exit(-1)
				#TODO Remove Zenity below
				outgps = commands.getstatusoutput("garmin_save_runs | zenity --progress --pulsate --text='Loading Data' auto-close")
				if outgps[0]==0: 
					# now we should have a lot of gmn (binary) files under $GARMIN_SAVE_RUNS
					foundFiles = self.searchFiles(self.tmpdir, "gmn")
					logging.info("Retrieved "+str(len(foundFiles))+" entries from GPS device")
					# discard old files
					selectedFiles = self.discardOld(foundFiles)
					# checking which entries are not imported yet
					self.listStringDBUTC = self.parent.parent.ddbb.select("records","date_time_utc")
					#logging.debug("From DB: "+str(self.listStringDBUTC))
					# commented out to fully rely on duplicates checking from garmintools plugin
					#selectedFiles = self.checkDupes(foundFiles)
					if selectedFiles is not None:
						logging.info("Dumping "+str(len(selectedFiles))+" binary files found")
						dumpFiles = self.dumpBinaries(selectedFiles)
						logging.info("Starting import")
						importFiles = self.importEntries(dumpFiles)
					else:
						logging.info("No new entries to add")
				else:
					logging.error("Error when retrieving data from GPS device")
			else:
				#TODO Remove Zenity below
				if numError == -1:
					os.popen("zenity --error --text='No Garmin device found\nCheck your configuration'");
				elif numError == -2:
					os.popen("zenity --error --text='Can not find garmintools binaries\nCheck your configuration'")			
		else: #No garmin device found
				#TODO Remove Zenity below
				os.popen("zenity --error --text='Can not handle Garmin device (wrong module loaded)\nCheck your configuration'");
		logging.info("Entries to import: "+str(len(importFiles)))		
		logging.debug("<<")
		return importFiles

	def discardOld(self, listEntries):
		tempList = []
		if self.deltaDays > 0:
			logging.info("Discarding entries older than "+str(self.deltaDays)+" days")
			limit = datetime.now() - timedelta(days = int(self.deltaDays))
			for entry in listEntries:
				filename = os.path.split(entry)[1].rstrip(".gmn")
				filenameDateTime = datetime.strptime(filename,"%Y%m%dT%H%M%S")
				logging.debug("Entry time: "+str(filenameDateTime)+" | limit: "+str(limit))
				if filenameDateTime < limit:
					logging.debug("Discarding old entry: "+str(filenameDateTime))
				else:
					tempList.append(entry)
		else:
			logging.info("Retrieving complete history from GPS device")
		return tempList

	def checkDupes(self, listEntries):
		""" The idea behind is building two lists: one with all date_time_utc from DB (need conversion to datetime!)
			and the other with all times from retrieved entries in UTC (need conversion from localtime -not possible only from filename- and to datetime!).
			Seconds are the keys in a populated Dict, so if already present in the system can be removed from the mapping structure.
			In case of legacy support, datetime from garmintools is older than (preceds) one stored in database (GPSBabel)
			so DTgarmintools + delta (~ 3 mins) >= DTgpsbabel.
			We obtain the final list retrieving remanent values from the dictionary """
		logging.debug(">>")
		tempList = []
		tempDict = {}
		for entry in listEntries:
			filename = os.path.split(entry)[1].rstrip(".gmn")
			filenameDateTime = datetime.strptime(filename,"%Y%m%dT%H%M%S")
			logging.debug("Entry time: "+str(filenameDateTime))
			tempDict[filenameDatetime] = filename
		
		stringStartDatetime = self.detailsFromFile(tree) # this time is localtime! (with timezone offset)
		exists = False
		if stringStartDatetime is not None:
			startDatetime = dateutil.parser.parse(stringStartDatetime)
			# converting to utc for proper comparison with date_time_utc
			utcStartDatetime = startDatetime.astimezone(tzutc()).strftime("%Y-%m-%dT%H:%M:%SZ")
			#ToDo. Think about best approach
		else:
			logging.debug("Not able to find start time, please check "+str(filename))
			exists = True # workaround for old/not correct entries (will crash at some point during import process otherwise)
		logging.debug("<<")
		return exists

	def importEntries(self, entries):
		# modified from garmintools plugin written by jb
		logging.debug(">>")
		logging.debug("Selected files: "+str(entries))
		importfiles = []
		for filename in entries:
			if self.valid_input_file(filename):
				#Garmin dump files are not valid xml - need to load into a xmltree
				#read file into string
				with open(filename, 'r') as f:
					xmlString = f.read()
				fileString = StringIO.StringIO("<root>"+xmlString+"</root>")
				#parse string as xml
				tree = etree.parse(fileString)
				#if not self.inDatabase(tree, filename):
				if not self.entryExists(tree, filename):
					sport = self.getSport(tree)
					gpxfile = "%s/garmintools-%d.gpx" % (self.tmpdir, len(importfiles))					
					self.createGPXfile(gpxfile, tree)
					importfiles.append((gpxfile, sport))
				else:
					logging.debug("%s already present. Skipping import." % (filename,) )
			else:
				logging.error("File %s failed validation" % (filename))
		logging.debug("<<")
		return importfiles

	def valid_input_file(self, filename):
		""" Function to validate input file if requested"""
		if not self.validate:  #not asked to validate
			logging.debug("Not validating %s" % (filename) )
			return True
		else:
			logging.debug("Cannot validate garmintools dump files yet")
			return True
			'''xslfile = os.path.realpath(self.parent.parent.data_path)+ "/schemas/GarminTrainingCenterDatabase_v2.xsd"
			from lib.xmlValidation import xmlValidator
			validator = xmlValidator()
			return validator.validateXSL(filename, xslfile)'''

	def entryExists(self, tree, filename):
		stringStartDatetime = self.detailsFromFile(tree) # this time is localtime! (with timezone offset)
		exists = False
		if stringStartDatetime is not None:
			startDatetime = dateutil.parser.parse(stringStartDatetime)
			# converting to utc for proper comparison with date_time_utc
			stringStartUTC = startDatetime.astimezone(tzutc()).strftime("%Y-%m-%dT%H:%M:%SZ")
			if self.legacyComp:
				#ToDo
				# All entries in UTC, so similars must have same date (startsWith)
				exists = False
			else:
				if (stringStartUTC,) in self.listStringDBUTC: # strange way to store results from DB
					exists = True
				else:
					logging.info("Marking "+str(filename)+" | "+str(stringStartUTC)+" to import")
					exists = False
		else:
			logging.debug("Not able to find start time, please check "+str(filename))
			exists = True # workaround for old/not correct entries (will crash at some point during import process otherwise)
		return exists

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
			stringStartDatetime = pointElement.get("time")
			return stringStartDatetime
		return None

	def createGPXfile(self, gpxfile, tree):
		""" Function to transform a Garmintools dump file to a valid GPX+ file
		"""
		xslt_doc = etree.parse(self.data_path+"/translate.xsl")
		transform = etree.XSLT(xslt_doc)
		result_tree = transform(tree)
		result_tree.write(gpxfile, xml_declaration=True)

	def dumpBinaries(self, listFiles):
		logging.debug(">>")
		dumpFiles=[]
		for filename in listFiles:
			outdump = filename.replace('.gmn', '.dump')
			logging.debug("outdump: "+str(outdump))
			result = commands.getstatusoutput("garmin_dump %s > %s" %(filename,outdump))
			if result[0] == 0:
				dumpFiles.append(outdump)
			else:
				logging.error("Error when creating dump of "+str(filename)+": "+str(result))
		logging.debug("<<")
		return dumpFiles

	def searchFiles(self, rootPath, extension):
		logging.debug(">>")
		foundFiles=[]
		logging.debug("rootPath: "+str(rootPath))
		result = commands.getstatusoutput("find %s -name *.%s" %(rootPath,extension))
		if result[0] == 0:
			foundFiles = result[1].splitlines()
			#logging.debug("Found files: "+str(foundFiles))
			logging.info ("Found files: "+str(len(foundFiles)))
		else:
			logging.error("Not able to locate files from GPS: "+str(result))
		logging.debug("<<")
		return foundFiles

	def getDeviceInfo(self):
		logging.debug(">>")
		result = commands.getstatusoutput('garmin_get_info')
		logging.debug("Returns "+str(result))
		numError = 0
		if result[0] == 0:
			if result[1] != "garmin unit could not be opened!":
				try:
					#ToDo: review, always get "lxml.etree.XMLSyntaxError: PCDATA invalid Char value 28, line 6, column 29" error
					xmlString = result[1].rstrip()
					logging.debug("xmlString: "+str(xmlString))
					prueba = etree.XMLID(xmlString)
					logging.debug("Prueba: "+str(prueba))
					tree = etree.fromstring(xmlString)
					description = self.getProductDesc(tree)
					if description is not None:
						logging.info("Found "+str(description))
					else:
						raise Exception
				except:
					logging.error("Not able to identify GPS device. Continuing anyway...")
					pass
			else:
				logging.error(result[1])
				numError = -1
		else:
			logging.error("Can not find garmintools binaries, please check your installation")
			numError = -2
		logging.debug("<<")
		return numError

	def getProductDesc(self, tree):
		root = tree.getroot()
		pointProduct = root.find(".//garmin_product")
		if pointProduct is not None:
			desc = pointProduct.get("product_description")
			return desc
		return None

	def checkLoadedModule(self):
		try:
			outmod = commands.getstatusoutput('/sbin/lsmod | grep garmin_gps')
			if outmod[0]==256:	#there is no garmin_gps module loaded
				return True
			else:
				return False
		except:
			return False

	def createUserdirBackup(self):
		logging.debug('>>')
		result = commands.getstatusoutput('tar -cvzf '+os.environ['HOME']+'/pytrainer_`date +%Y%m%d_%H%M`.tar.gz '+self.confdir)
		if result[0] != 0:
			raise Exception, "Copying current user directory does not work, error #"+str(result)
		else:
			logging.info('User directory backup successfully created')
		logging.debug('<<')

