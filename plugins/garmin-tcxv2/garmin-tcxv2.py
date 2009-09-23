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
import libxml2
import libxslt

class garminTCXv2():
	def __init__(self, parent = None):
		self.parent = parent
		self.tmpdir = self.parent.conf.getValue("tmpdir")

	def run(self):
		logging.debug(">>")
		# able to select multiple files....
		f = os.popen("zenity --file-selection --multiple --title 'Choose a TCX file to import'")
		inputData = f.read().strip()
		inputfiles = inputData.split('|')
		xslfile= os.path.dirname(os.path.realpath(__file__)) + "/translate.xsl"
		outputfile=[]
		if os.path.isfile(xslfile):
			for index in range(len(inputfiles)):
				outputfile.append(self.tmpdir+"/outputfile"+str(index)+".gpx")
				inputfile=inputfiles[index]
				if os.path.isfile(inputfile):
					styledoc = libxml2.parseFile(xslfile)
					style = libxslt.parseStylesheetDoc(styledoc)
					doc = libxml2.parseFile(inputfile)
					result = style.applyStylesheet(doc, None)
					style.saveResultToFilename(outputfile[index], result, 0)
					style.freeStylesheet()
					doc.freeDoc()
					result.freeDoc()
				else:
					raise Exception("XML input file not found, looking for: " + inputfile)
		else:
			raise Exception("XSL file not found, looking for: " + xslfile)
		logging.debug("<<")
		return outputfile

