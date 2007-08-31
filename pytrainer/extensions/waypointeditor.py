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


class WaypointEditor:
	def __init__(self, data_path = None, vbox = None, waypoint=None):
		self.data_path = data_path
		self.conf = checkConf()
		self.extension = Extension()
		self.moz = gtkmozembed.MozEmbed()
                vbox.pack_start(self.moz, True, True)
		vbox.show_all()
		self.htmlfile = ""
		self.waypoint=waypoint
	
	def drawMap(self):
		#self.createHtml()
		tmpdir = self.conf.getValue("tmpdir")
		htmlfile = tmpdir+"/waypointeditor.html"
        	self.moz.load_url("file://"+htmlfile)
	
	def createHtml(self,default_waypoint=None):
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
		var pytrainerAPI = new SOAPCall();
		netscape.security.PrivilegeManager.enablePrivilege("UniversalBrowserRead");
    		pytrainerAPI.transportURI = "http://localhost:8081/";

		var param1 = new SOAPParameter();
  		param1.name = "lon";
  		param1.value = lon;
 
		var param2 = new SOAPParameter();
  		param2.name = "lat";
  		param2.value = lat;
 
  		var parameters = [param1,param2];
		pytrainerAPI.encode(0,
                	"addWaypoint", null,
                  	0, null,
                  	parameters.length, parameters);
		
		var response = pytrainerAPI.invoke();

		if(response.fault){
  			alert("An error occured: " + response.fault.faultString);
			return 0;
			} 
		else {
  			var re = new Array();
  			re = response.getParameters(false, {});
			}
		return re[0].value;
  		}  	
	
	function updateWaypoint(lon,lat,id) {
		var pytrainerAPI = new SOAPCall();
		netscape.security.PrivilegeManager.enablePrivilege("UniversalBrowserRead");
    		pytrainerAPI.transportURI = "http://localhost:8081/";

		var param1 = new SOAPParameter();
  		param1.name = "lon";
  		param1.value = lon;
 
		var param2 = new SOAPParameter();
  		param2.name = "lat";
  		param2.value = lat;
		
		var param3 = new SOAPParameter();
  		param3.name = "id_waypoint";
  		param3.value = id;
 
  		var parameters = [param1,param2,param3];
		pytrainerAPI.encode(0,
                	"updateWaypoint", null,
                  	0, null,
                  	parameters.length, parameters);
		
		var response = pytrainerAPI.invoke();

		if(response.fault){
  			alert("An error occured: " + response.fault.faultString);
			} 
		else {
  			var re = new Array();
  			re = response.getParameters(false, {});
  			//alert("Return value: " + re[0].value);
			}
  		}  	

	function createMarker(waypoint) {
		var lon = waypoint[0];
		var lat = waypoint[1];
		var id = waypoint[5];
		
		var point = new GLatLng(lat,lon);
		var text = "<b>"+waypoint[2]+"</b><br/>"+waypoint[3];

		var icon = new GIcon();
		icon.image = "http://labs.google.com/ridefinder/images/mm_20_red.png";
		icon.shadow = "http://labs.google.com/ridefinder/images/mm_20_shadow.png";
		icon.iconSize = new GSize(12, 20);
		icon.shadowSize = new GSize(22, 20);
		icon.iconAnchor = new GPoint(6, 20);
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



