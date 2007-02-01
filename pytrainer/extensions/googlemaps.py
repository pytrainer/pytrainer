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

import gtkmozembed
import os

from pytrainer.lib.system import checkConf
from pytrainer.extension import Extension

class Googlemaps:
	def __init__(self, data_path = None, vbox = None):
		self.data_path = data_path
		self.conf = checkConf()
		self.extension = Extension()
		self.moz = gtkmozembed.MozEmbed()
                vbox.pack_start(self.moz, True, True)
		vbox.show_all()
		self.htmlfile = ""
	
	def drawMap(self,id_record):
		code = "googlemapsviewer"
		extensiondir = self.conf.getValue("extensiondir")
		cachefile = extensiondir+"/"+code+"/%d.gpx" %id_record
		if not os.path.isfile(cachefile):
			trackdistance = self.extension.getCodeConfValue(code,"Trackdistance")
			gpxfile = self.conf.getValue("gpxdir")+"/%s.gpx" %id_record
			os.system("gpsbabel -t -i gpx -f %s -x position,distance=%sm -o gpx -F %s" %(gpxfile,trackdistance,cachefile))

		key = self.extension.getCodeConfValue(code,"googlekey")
		htmlfile = self.data_path+"/maps/index.html?gpxfile="+cachefile+"&key="+key
		htmlfile = os.path.abspath(htmlfile)
		if htmlfile != self.htmlfile:
        		self.moz.load_url("file://"+htmlfile)
			self.htmlfile = htmlfile
		else:
			pass

