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
from pytrainer.extension import Extension
from pytrainer.lib.fileUtils import fileUtils

import string,cgi,time
import time

import logging

class WaypointEditor:
	def __init__(self, data_path = None, vbox = None, waypoint=None):		
		logging.debug(">>")
		self.data_path = data_path
		self.conf = checkConf()
		self.extension = Extension()
		self.moz = gtkmozembed.MozEmbed()
		self.moz.connect('title', self.handle_title_changed) 
		vbox.pack_start(self.moz, True, True)
		vbox.show_all()
		self.htmlfile = ""
		self.waypoint=waypoint
		logging.debug("<<")
		
	def handle_title_changed(self, *args): 
		title = self.moz.get_title() 
		print "Received title", title
		m = re.match("call:([a-zA-Z]*)[(](.*)[)]", title) 
		if m: 
			fname = m.group(1) 
			args = m.group(2) 
			if fname == "addWaypoint": 
				am = re.match("([+-]?[0-9]+[.][0-9]+),([+-]?[0-9]+[.][0-9]+)", args) 
				if am: 
					lon, lat = am.group(1), am.group(2) 
					lon, lat = float(lon), float(lat) 
					self.waypoint.addWaypoint(lon, lat, "NEW WAYPOINT") 
				else: 
					raise ValueError("Error parsing addWaypoint parameters: %s" % args) 
			elif fname == "updateWaypoint": 
				am = re.match("([+-]?[0-9]+[.][0-9]+),([+-]?[0-9]+[.][0-9]+),([0-9]*)", args) 
				if am: 
					lon, lat, id_waypoint = am.group(1), am.group(2), am.group(3) 
					lon, lat, id_waypoint = float(lon), float(lat), int(id_waypoint) 
					retorno = self.waypoint.getwaypointInfo(id_waypoint) 
					if retorno: 
						name, comment, sym = retorno[0][5], retorno[0][3], retorno[0][6] 
						self.waypoint.updateWaypoint(id_waypoint, lat, lon, name, comment, sym) 
					else: 
						raise KeyError("Unknown waypoint id %d", id_waypoint) 
					self.waypoint.addWaypoint(lon, lat, "NEW WAYPOINT") 
				else: 
					raise ValueError("Error parsing addWaypoint parameters: %s" % args) 
			else: 
				raise ValueError("Unexpected function name %s" % fname) 
		return False 
	
	def drawMap(self):
		logging.debug(">>")
		#self.createHtml()
		tmpdir = self.conf.getValue("tmpdir")
		htmlfile = tmpdir+"/waypointeditor.html"
		logging.debug("HTML file: "+str(htmlfile))
		self.moz.load_url("file://"+htmlfile)
		logging.debug("<<")
	
	def createHtml(self,default_waypoint=None):
		logging.debug(">>")
		tmpdir = self.conf.getValue("tmpdir")
		filename = tmpdir+"/waypointeditor.html"
	
		points = self.waypoint.getAllWaypoints()
		londef = 0
		latdef = 0
		content = """

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"  xmlns:v="urn:schemas-microsoft-com:vml">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
    <title>edit waypoints</title>

    <script id="googleapiimport" src="http://maps.google.com/maps?file=api&amp;v=2"
            type="text/javascript"></script>
    <script type="text/javascript">
"""
		i = 0
		arrayjs = ""
		if default_waypoint is None and points: 
			default_waypoint = points[0][0]
		for point in points:
			if point[0] == default_waypoint:
				londef = point[2]
				latdef = point[1]
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
	is_addmode = 0;
    //<![CDATA[

	function addWaypoint(lon,lat) {
		document.title = "call:addWaypoint(" + lon + "," + lat + ")";
  		}  	
	
	function updateWaypoint(lon,lat,id) {
		document.title = "call:updateWaypoint(" + lon + "," + lat + "," + id + ")"; 
  		}  	

	function createMarker(waypoint) {
		var lon = waypoint[0];
		var lat = waypoint[1];
		var id = waypoint[5];
		var sym = waypoint[4];
		
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
		
		var markerD = new GMarker(point, {icon:icon, draggable: true}); 
		map.addOverlay(markerD);

		markerD.enableDragging();

		GEvent.addListener(markerD, "mouseup", function(){
			position = markerD.getPoint();
			updateWaypoint(position.lng(),position.lat(),id);
		});
  		return markerD;
		}

	function load() {
		if (GBrowserIsCompatible()) {
			//Dibujamos el mapa
			map = new GMap2(document.getElementById("map"));
        		map.addControl(new GLargeMapControl());
        		map.addControl(new GMapTypeControl());
			map.addControl(new GScaleControl());
	"""
		if londef != 0:
        		content +="""
				lon = %s;
				lat = %s;
				""" %(londef,latdef)
		else:
			 content += """
				lon = 0;
				lat = 0;
				"""
		content +="""
			map.setCenter(new GLatLng(lat, lon), 11);

			//Dibujamos el minimapa
			ovMap=new GOverviewMapControl();
			map.addControl(ovMap);
			mini=ovMap.getOverviewMap();

			//Dibujamos los waypoints
			for (i=0; i<waypointList.length; i++){
  				createMarker(waypointList[i]);
				map.enableDragging();
				}

			//Preparamos los eventos para anadir nuevos waypoints
			GEvent.addListener(map, "click", function(marker, point) {
    				if (is_addmode==1){
					map.enableDragging();
					//map.addOverlay(new GMarker(point));
					var lon = point.lng();
					var lat = point.lat();
				
					var waypoint_id = addWaypoint(lon,lat);
					var waypoint = Array (lon,lat,"","","",waypoint_id);
  					createMarker(waypoint);
					is_addmode = 0;
					}
				});
      			}
    		}	

	function addmode(){
		is_addmode = 1;
		map.disableDragging();
		}

    //]]>
    </script>
<style>
.form {
	position: absolute;
	top: 200px;
	left: 300px;
	background: #ffffff;
	}
</style>

  </head>
  <body onload="load()" onunload="GUnload()" style="cursor:crosshair" border=0>
    		<div id="map" style="width: 100%; height: 460px; top: 0px; left: 0px"></div>
    		<div id="addButton" style="position: absolute; top: 32px;left: 86px;">
			<input type="button" value="New Waypoint" onclick="javascript:addmode();">
		</div>


  </body>
</html>
"""
		file = fileUtils(filename,content)
		file.run()
		logging.debug("<<")


