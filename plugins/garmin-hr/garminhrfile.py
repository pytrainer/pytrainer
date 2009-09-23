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
import logging
import commands

from lib.xmlUtils import XMLParser
from lib.gpx import Gpx

class garminhrfile():
	def __init__(self, parent = None):
		self.parent = parent
		self.tmpdir = self.parent.conf.getValue("tmpdir")

	def run(self):
		f = os.popen("zenity --file-selection --title 'Choose a Garmin Training Center file to import'")
		gtrnctrFile = f.read().strip()

		# XML file from gpsbabel refers to schemas and namespace definitions which are no longer available, removing this info - dgg - 12.05.2008
		# check to see if we can remove this...
		gtrnctrFileMod = removeHeaders(gtrnctrFile)
		print "modified gtrnctrfile: " + gtrnctrFileMod
		
		return [gtrnctrFileMod,] #TODO this is where the conversion and checking will occur

		def removeHeaders(gtrnctrFile):
			if os.path.isfile(gtrnctrFile):
				gtrnctrFileMod = self.tmpdir+"/file_mod.gtrnctr"
				f = open(gtrnctrFile,"r")
				lines = f.readlines()
				f.close()
				f = open(gtrnctrFileMod,'w')
				headers = lines[0]+'<TrainingCenterDatabase>\n'
				f.write(headers)
				f.write(''.join(lines[6:]))
				f.close()
				return gtrnctrFileMod
			else:
				return None

		def importFromGTRNCTR(self,gtrnctrFile):
			"""22.03.2008 - dgranda
			Retrieves sport, date and start time from each entry coming from GPS
			and compares with what is stored locally, just to import new entries
			31.08.2008 - dgranda - Only checks start time, discarding sport info
			args: file with data from GPS file (garmin format)
			returns: none"""
			logging.debug('>>')
			logging.info('Retrieving data from '+gtrnctrFile)
			xmlParser=XMLParser(gtrnctrFile)
			listTracksGPS = xmlParser.shortFromGPS(gtrnctrFile, True)
			logging.info('GPS: '+str(len(listTracksGPS))+' entries found')
			if len(listTracksGPS)>0:
				listTracksLocal = self.shortFromLocalDB(True)
				logging.info('Local: '+str(len(listTracksLocal))+' entries found')
				listNewTracks=self.compareTracks(listTracksGPS,listTracksLocal,False)
				newTracks = len(listNewTracks)
				# empty constructor for Gpx 
				gpx = Gpx()
				i=0
				for entry in listNewTracks:
					i=i+1
					logging.debug('Entry summary to import: '+str(entry))
					newGPX=gpx.retrieveDataFromGTRNCTR(gtrnctrFile, entry)
					entry_id = self.insertNewRecord(newGPX, entry)
					logging.info('Entry '+str(entry_id)+' has been added ('+str(i)+'/'+str(newTracks)+')')
			else:
				logging.info('No tracks found in GPS device')
			logging.debug('<<')
