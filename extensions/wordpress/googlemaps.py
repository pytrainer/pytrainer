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
import re
import sys
import fileinput
import shutil

import pytrainer.lib.points as Points
from pytrainer.lib.gpx import Gpx
from  pytrainer.lib.fileUtils import fileUtils

	
def drawMap(gpxfile,key,htmlpath):
	#Not sure why need to process gpx file
	cachefile = "/tmp/gpx.txt"
	#trackdistance = 100
	#os.system("gpsbabel -t -i gpx -f %s -x position,distance=%sm -o gpx -F %s" %(gpxfile,trackdistance,cachefile))
	shutil.copy2(gpxfile, cachefile)

	# Test if file already contains gpxdata attribute
	found = False
	for line in fileinput.FileInput(cachefile,inplace=1):
		if "xmlns:gpxdata" in line:
			found = True
		print line.rstrip('\n');
	# If file don't has gpxdata attribute: add namespace
	if not found:
		for line in fileinput.FileInput(cachefile,inplace=1):
			if "xmlns:xsi" in line:
				line=line.replace('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"','xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0"')
			print line.rstrip('\n');
	gpx = Gpx("",cachefile)
	list_values = gpx.getTrackList()
	pointlist = []
	for i in list_values:
		pointlist.append((i[4],i[5]))
	points,levels = Points.encodePoints(pointlist)
	points = points.replace("\\","\\\\")
	
	createHtml(points,levels,pointlist[0],htmlpath,key)
	
def createHtml(points,levels,init_point,htmlpath,key):
	content = "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \n"
	content += "		\"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">\n"
	content += "	<html xmlns=\"http://www.w3.org/1999/xhtml\"  xmlns:v=\"urn:schemas-microsoft-com:vml\">\n"
	content += "	<head>\n"
	content += "		<meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\"/>\n"
	content += "		<title>Google Maps JavaScript API Example</title>\n"
	content += "		<script id=\"googleapiimport\" src=\"http://maps.google.com/maps?file=api&amp;v=2&amp;key=%s\"\n" %key
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
	content += "		<div id=\"map\" style=\"width: 460px; height: 460px\"></div>\n"
	content += "	</body>\n"
	content += "</html>\n" 
	file = fileUtils(htmlpath,content)
	file.run()
		

