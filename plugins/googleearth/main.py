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


import os
import commands
import logging
from lxml import etree
from pytrainer.gui.dialogs import fileChooserDialog, guiFlush

class googleearth():
	def __init__(self, parent = None, validate=False):
		self.parent = parent
		self.pytrainer_main = parent.pytrainer_main
		self.validate = validate
		self.data_path = os.path.dirname(__file__)
		self.tmpdir = self.pytrainer_main.profile.tmpdir

	def run(self):
		logging.debug(">>")
		selectedFiles = fileChooserDialog(title="Choose a Google Earth file (.kml) to import", multiple=True).getFiles()
		guiFlush()
		importfiles = []
		if not selectedFiles:
			return importfiles
		for filename in selectedFiles:
			if self.valid_input_file(filename):
				if not self.inDatabase(filename):
					sport = self.getSport(filename) #TODO Fix sport determination
					gpxfile = "%s/googleearth-%d.gpx" % (self.tmpdir, len(importfiles))	
					outgps = commands.getstatusoutput("gpsbabel -t -i kml -f %s -o gpx -F %s" % (filename, gpxfile) )
					#self.createGPXfile(gpxfile, filename) #TODO Fix processing so not dependant on the broken gpsbabel
					importfiles.append((gpxfile, sport))
				else:
					logging.debug("%s already in database. Skipping import." % (filename) )
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
			return True
			#TODO need to check schema and validation for example kml files
			#xslfile = os.path.realpath(self.parent.parent.data_path)+ "/schemas/ogckml22.xsd"
			#from pytrainer.lib.xmlValidation import xmlValidator
			#validator = xmlValidator()
			#return validator.validateXSL(filename, xslfile)
	
	def inDatabase(self, filename):
		""" Function to determine if a given file has already been imported into the database
		    only compares date and start time (sport may have been changed in DB after import)
		"""
		#time = self.detailsFromKML(filename)
		#if self.parent.parent.ddbb.select("records","*","date_time_utc=\"%s\"" % (time)):
		#	return True
		#else:
		return False
			
	def getSport(self, filename):
		#TODO Fix sport determination
		return "Run"
		
	def detailsFromKML(self, filename):
		""" Function to return the first time element from a KML file """
		#TODO
		#tree = xml.etree.cElementTree.ElementTree(file=filename)
		#root = tree.getroot()
		#timeElement = root.find(".//{http://www.topografix.com/GPX/1/1}time")
		#if timeElement is None:
		#	return None
		#else:
		#	return timeElement.text
		
	def createGPXfile(self, gpxfile, filename):
		''' Function to transform a GPSBabel kml file to a valid GPX+ file
		'''
		#TODO!!
		xslt_doc = etree.parse(self.data_path+"/translate.xsl")
		transform = etree.XSLT(xslt_doc)
		result_tree = transform(filename)
		result_tree.write(gpxfile, xml_declaration=True)

