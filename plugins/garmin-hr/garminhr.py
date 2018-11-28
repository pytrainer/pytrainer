#!/usr/bin/env python
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

import os, sys
import logging
from lxml import etree
from pytrainer.lib.xmlUtils import XMLParser
from pytrainer.core.activity import Activity
from sqlalchemy.orm import exc

import subprocess

class garminhr():
	""" Plugin to import from a Garmin device using gpsbabel
		Checks each activity to see if any entries are in the database with the same start time
		Creates GPX files for each activity not in the database

		Note: using lxml see http://codespeak.net/lxml
	"""
	def __init__(self, parent = None, validate=False):
		self.parent = parent
		self.pytrainer_main = parent.pytrainer_main
		self.tmpdir = self.pytrainer_main.profile.tmpdir
		self.data_path = os.path.dirname(__file__)
		self.validate = validate
		self.input_dev = self.getConfValue("device")
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

	def error_dialog(self, msg):
		#TODO Remove Zenity below
		subprocess.call(["zenity", "--error",
		                 "--text='%s'" % msg])

	def run(self):
		logging.debug(">>")
		importfiles = []
		no_device_msg = ("Can not handle Garmin device\n"
		                 "Check your configuration\n"
		                 "Current USB port is set "
		                 "to:\t %s" % self.input_dev)

		if not self.checkGPSBabelVersion("1.3.5"):
			self.error_dialog("Must be using version 1.3.5 "
			                  "of GPSBabel for this plugin")
		elif self.garminDeviceExists():
			try:
				gpsbabelOutputFile = "%s/file.gtrnctr" % (self.tmpdir)
				#TODO Remove Zenity below
				outgps = subprocess.Popen(
				        "gpsbabel -t -i garmin -f %s -o gtrnctr -F %s "
				        "| zenity --progress --pulsate --text='Loading Data' "
				        "    auto-close" % (self.input_dev, gpsbabelOutputFile),
				        stdout=subprocess.PIPE,
				        stderr=subprocess.PIPE,
				        shell=True)
				stdout, stderr = outgps.communicate()
				if outgps.returncode == 0:
					if stdout == "Found no Garmin USB devices.": # check localizations
						error_msg = "GPSBabel found no Garmin USB devices"
						logging.error(error_msg)
						self.error_dialog(error_msg)
					else: #gpsbabel worked - now process file...
						if self.valid_input_file(gpsbabelOutputFile):
							for (sport, tracks) in self.getTracks(gpsbabelOutputFile):
								logging.debug("Found %d tracks for %s sport in %s" % (len(tracks), sport, gpsbabelOutputFile))
								count = 0
								for track in tracks: #can be multiple tracks
									if self.shouldImport(track):
										count += 1
										gpxfile = "%s/garminhrfile%d.gpx" % (self.tmpdir, len(importfiles))
										self.createGPXfile(gpxfile, track)
										if self.sport: #Option to overide sport is set
											importfiles.append((gpxfile, self.sport))
										else: #Use sport from file
											importfiles.append((gpxfile, sport))
								logging.debug("Importing %d of %d tracks for sport %s" % (count, len(tracks), sport) )
						else:
							logging.info("File %s failed validation" % (gpsbabelOutputFile))
			except Exception:
				self.dialog_msg(no_device_msg)
				print sys.exc_info()[0]
		else: #No garmin device found
			self.error_dialog(no_device_msg)
		logging.debug("<<")
		return importfiles

	def checkGPSBabelVersion(self, validVersion):
		process = subprocess.Popen(['gpsbabel', '-V'],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
		stdout, stderr = process.communicate()
		if process.returncode == 0:
			version = stdout.split()
			try:
				if version[2] == validVersion:
					return True
				else:
					logging.error("GPSBabel at version %s instead of expected version %s" % (version[2], validVersion))
			except:
				logging.error("Unexpected result from gpsbabel -V")
				return False
		return False

	def garminDeviceExists(self):
		try:
			process = subprocess.Popen('lsmod | grep garmin_gps',
			                           stdout=subprocess.PIPE,
			                           stderr=subprocess.PIPE,
			                           shell=True)
			stdout, stderr = process.communicate()
			# stdout is empty if no garmin_gps module is loaded
			if stdout != '':
				self.input_dev = "usb:"
				return True
			else:
				return False
		except:
			return False

	def valid_input_file(self, filename):
		""" Function to validate input file if requested"""
		if not self.validate: #not asked to validate
			logging.debug("Not validating %s" % (filename) )
			return True
		else: #Validate TCXv1, note are validating against gpsbabels 'broken' result...
			xslfile = os.path.realpath(self.pytrainer_main.data_path)+ "/schemas/GarminTrainingCenterDatabase_v1-gpsbabel.xsd"
			from lib.xmlValidation import xmlValidator
			validator = xmlValidator()
			return validator.validateXSL(filename, xslfile)

	def getTracks(self, filename):
		""" Function to return all the tracks in a Garmin Training Center v1 file
		"""
		sportsList = ("Running", "Biking", "Other", "MultiSport")
		result = []
		tree = etree.ElementTree(file=filename)
		root = tree.getroot()
		for sport in sportsList:
			try:
				sportLevel = root.find(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v1}%s" % sport)
				tracks = sportLevel.findall(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v1}Track")
				result.append((sport, tracks))
			except:
				print "No entries for sport %s" % sport
		return result

	def shouldImport(self, track):
		""" Function determines whether a track should be imported or not
			Currently using time only
		"""
		timeElement = track.find(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v1}Time")
		if timeElement is None:
			#print (etree.tostring(track, pretty_print=True))
			logging.debug("Error no time found in track")
			return False
		else:
			time = timeElement.text
			try:
				self.pytrainer_main.ddbb.session.query(Activity).filter(Activity.date_time_utc == time).one()
				return False
			except exc.NoResultFound:
				return True

	def createGPXfile(self, gpxfile, track):
		""" Function to transform a Garmin Training Center v1 Track to a valid GPX+ file
		"""
		xslt_doc = etree.parse(self.data_path+"/translate.xsl")
		transform = etree.XSLT(xslt_doc)
		result_tree = transform(track)
		result_tree.write(gpxfile, xml_declaration=True, encoding='UTF-8')



