#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#Copyright (C) 

#Based on plugin by Fiz Vazquez vud1@sindominio.net

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
import logging
from lxml import etree

from gui.dialogs import fileChooserDialog, guiFlush


class garminhrfile():
	""" Plugin to import from a Garmin Training Center (version 1) file (as outputed from gpsbabel)
		Can have multiple activities in the file
		Checks to each activity to see if any entries are in the database with the same start time
		Creates GPX files for each activity not in the database

		Note: using lxml see http://codespeak.net/lxml
	"""
	def __init__(self, parent = None):
		self.parent = parent
		self.tmpdir = self.parent.conf.getValue("tmpdir")
		self.data_path = os.path.dirname(__file__)

	def run(self):
		selectedFiles = fileChooserDialog(title="Choose a Garmin Training Center file to import").getFiles()
		guiFlush()
		importfiles = []
		if not selectedFiles:
			return importfiles
		for filename in selectedFiles: #could be multiple files selected - currently only single selection enabled
			tracks = self.getTracks(filename)
			logging.debug("Found %d tracks in %s" % (len(tracks), filename))
			for track in tracks: #can be multiple tracks
				if shouldImport(track):
					gpxfile = "%s/garminhrfile%d.gpx" % (self.tmpdir, len(importfiles))
					self.createGPXfile(gpxfile, track)
					importfiles.append(gpxfile)
		return importfiles

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
			#comparing date and start time (sport may have been changed in DB after import)
			if self.parent.parent.ddbb.select("records","*","date_time_utc=\"%s\"" % (time)):
				return True
			else:
				return False

	def getTracks(self, filename):
		""" Function to return all the tracks in a Garmin Training Center v1 file
		"""
		tree = etree.ElementTree(file=filename)
		root = tree.getroot()
		tracks = root.findall(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v1}Track")
		return tracks

	def createGPXfile(self, gpxfile, track):
		""" Function to transform a Garmin Training Center v1 Track to a valid GPX file
		"""
		xslt_doc = etree.parse(self.data_path+"/translate.xsl")
		transform = etree.XSLT(xslt_doc)
		result_tree = transform(track)
		result_tree.write(gpxfile)

