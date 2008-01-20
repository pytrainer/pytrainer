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
	def __init__(self, data_path = None, vbox = None, waypoint = None):
		self.data_path = data_path
		self.conf = checkConf()
		self.moz = gtkmozembed.MozEmbed()
                vbox.pack_start(self.moz, True, True)
		vbox.show_all()
		self.htmlfile = ""
		self.waypoint=waypoint
	
	def drawMap(self,id_record):
		code = "googlemapsviewer"
		extensiondir = self.conf.getValue("extensiondir")+"/"+code
		if not os.path.isdir(extensiondir):
            		os.mkdir(extensiondir)
		points = []
		levels = []
		pointlist = []
		htmlfile = self.conf.getValue("tmpdir")+"/index.html"
		
		gpxfile = self.conf.getValue("gpxdir")+"/%s.gpx" %id_record
		if os.path.isfile(gpxfile):
			gpx = Gpx(self.data_path,gpxfile)
			list_values = gpx.getTrackList()
			for i in list_values:
				pointlist.append((i[4],i[5]))
			points,levels = Points.encodePoints(pointlist)
			points = points.replace("\\","\\\\")
	
			self.createHtml(points,levels,pointlist[0])
			htmlfile = os.path.abspath(htmlfile)
			if htmlfile != self.htmlfile:
        			self.moz.load_url("file://"+htmlfile)
		else:
			self.createErrorHtml()
        		self.moz.load_url("file://"+htmlfile)
		#	self.htmlfile = htmlfile
		#else:
		#	pass
	
	def createHtml(self,points,levels,init_point):
		waypoints = self.waypoint.getAllWaypoints()
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
		i = 0
		arrayjs = ""
		for point in waypoints:
			content += "lon = '%f';\n"%point[2]
			content += "lat = '%f';\n"%point[1]
			content += "name = '%s';\n"%point[6]
			content += "description = '%s';\n"%point[4]
			content += "sym = '%s';\n"%point[7]
			content += "id = '%d';\n"%point[0]
			content += """waypoint%d = Array (lon,lat,name,description,sym,id);\n"""%i
			if i>0:
				arrayjs+=","
			arrayjs +="waypoint%d"%i
			i = i+1
		content += """waypointList = Array (%s);\n""" %arrayjs
		content += """
	function createMarker(waypoint,map) {
		var lon = waypoint[0];
		var lat = waypoint[1];
		var id = waypoint[5];
		var name = waypoint[2];
		var description = waypoint[3];
		
		var point = new GLatLng(lat,lon);
		var text = "<b>"+waypoint[2]+"</b><br/>"+waypoint[3];

		var icon = new GIcon();
		if (sym=="Summit") {
			icon.image = \""""+os.path.abspath(self.data_path)+"""/glade/summit.png\";
			}
		else {
			icon.image = \""""+os.path.abspath(self.data_path)+"""/glade/waypoint.png\";
			}
		icon.iconSize = new GSize(32, 32);
		icon.iconAnchor = new GPoint(16, 16);
		icon.infoWindowAnchor = new GPoint(5, 1);
		
		var markerD = new GMarker(point, {icon:icon, draggable: false}); 
		GEvent.addListener(markerD, "click", function() {
            		markerD.openInfoWindowHtml("<b>" + name + "</b><br/>"+description);
          		});
		map.addOverlay(markerD);

		}"""

		content += "		function load() {\n"
		content += "			if (GBrowserIsCompatible()) {\n"
        	content += "				var map = new GMap2(document.getElementById(\"map\"));\n"
        	content += "				map.addControl(new GLargeMapControl());\n"
        	content += "				map.addControl(new GMapTypeControl());\n"
		content += "				map.addControl(new GScaleControl());\n"
        	content += "				map.setCenter(new GLatLng(%f,%f), 11);\n" %(float(init_point[0]),float(init_point[1]))
		content += "				ovMap=new GOverviewMapControl();\n"
		content += " 				map.addControl(ovMap);\n"
		content += "				mini=ovMap.getOverviewMap();\n"
		content += "				//Dibujamos los waypoints\n"
		content += "				for (i=0; i<waypointList.length; i++){\n"
 		content += " 					createMarker(waypointList[i],map);\n"
		content += "					map.enableDragging();\n"
		content += "					}\n"
		content += "				document.getElementById('map').style.top='0px';\n"
		content += "				document.getElementById('map').style.left='0px';\n"
		content += "				document.getElementById('map').style.width='100%';\n"
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
		
	def createErrorHtml(self):
		content = "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \n"
    		content += "		\"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">\n"
		content += "	<html xmlns=\"http://www.w3.org/1999/xhtml\"  xmlns:v=\"urn:schemas-microsoft-com:vml\">\n"
  		content += """	<head>\n
<body>
No Gpx Data
</body>
</html>
		"""
		tmpdir = self.conf.getValue("tmpdir")
		filename = tmpdir+"/index.html"
		file = fileUtils(filename,content)
		file.run()
