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
import re

from pytrainer.lib.system import checkConf
from pytrainer.lib.gpx import Gpx
import pytrainer.lib.points as Points 
from pytrainer.lib.fileUtils import fileUtils

class Googlemaps:
	def __init__(self, data_path = None, vbox = None):
		self.data_path = data_path
		self.conf = checkConf()
		self.moz = gtkmozembed.MozEmbed()
                vbox.pack_start(self.moz, True, True)
		vbox.show_all()
		self.htmlfile = ""
	
	def drawMap(self,id_record):
		code = "googlemapsviewer"
		extensiondir = self.conf.getValue("extensiondir")+"/"+code
		if not os.path.isdir(extensiondir):
            		os.mkdir(extensiondir)
		cachefile = extensiondir+"/%d.gpx" %id_record
		if not os.path.isfile(cachefile):
			trackdistance = "100"
			gpxfile = self.conf.getValue("gpxdir")+"/%s.gpx" %id_record
			os.system("gpsbabel -t -i gpx -f %s -x position,distance=%sm -o gpx -F %s" %(gpxfile,trackdistance,cachefile))

		gpx = Gpx(self.data_path,cachefile)
		list_values = gpx.getTrackList()
		pointlist = []
		for i in list_values:
			pointlist.append((i[4],i[5]))
		points,levels = Points.encodePoints(pointlist)
		points = points.replace("\\","\\\\")
	
		htmlfile = self.conf.getValue("tmpdir")+"/index.html"
		self.createHtml(points,levels,pointlist[0])
		htmlfile = os.path.abspath(htmlfile)
		if htmlfile != self.htmlfile:
        		self.moz.load_url("file://"+htmlfile)
		#	self.htmlfile = htmlfile
		#else:
		#	pass
	
	def createHtml(self,points,levels,init_point):
		tmpdir = self.conf.getValue("tmpdir")
		content = "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \n"
    		content += "		\"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">\n"
		content += "	<html xmlns=\"http://www.w3.org/1999/xhtml\"  xmlns:v=\"urn:schemas-microsoft-com:vml\">\n"
  		content += "	<head>\n"
    		content += "		<meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\"/>\n"
    		content += "		<title>Google Maps JavaScript API Example</title>\n"
    		content += "		<script id=\"googleapiimport\" src=\"http://maps.google.com/maps?file=api&amp;v=2\"\n"
            	content += "			type=\"text/javascript\"></script>\n"
    		content += "		<script type=\"text/javascript\">\n"
    		content += "		//<![CDATA[\n"
		content += "		function load() {\n"
		content += "			if (GBrowserIsCompatible()) {\n"
        	content += "				var map = new GMap2(document.getElementById(\"map\"));\n"
        	content += "				map.addControl(new GLargeMapControl());\n"
        	content += "				map.addControl(new GMapTypeControl());\n"
        	content += "				map.setCenter(new GLatLng(%s,%s), 11);\n" %(init_point[0],init_point[1])
        	content += "				// Add an encoded polyline.\n"
        	content += "				var encodedPolyline = new GPolyline.fromEncoded({\n"
		content += "					color: \"#3333cc\",\n"
		content += "					weight: 10,\n"
		content += "					points: \"%s\",\n" %points
		content += "					levels: \"%s\",\n" %levels
		content += "					zoomFactor: 32,\n"
		content += "					numLevels: 4\n"
		content += "					});\n"
		content += "				map.addOverlay(encodedPolyline);\n"
      		content += "				}\n"
    		content += "			}\n	"
    		content += "		//]]>\n"
    		content += "	</script>\n"
  		content += "	</head>\n"
  		content += "	<body onload=\"load()\" onunload=\"GUnload()\">\n"
    		content += "		<div id=\"map\" style=\"width: 520px; height: 480px\"></div>\n"
  		content += "	</body>\n"
		content += "</html>\n" 
		filename = tmpdir+"/index.html"
		file = fileUtils(filename,content)
		file.run()
		

