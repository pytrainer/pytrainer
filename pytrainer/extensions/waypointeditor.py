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
from pytrainer.lib.gpx import Gpx
import pytrainer.lib.points as Points 
from pytrainer.lib.fileUtils import fileUtils

import string,cgi,time
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from threading import Thread

class MyHandler(BaseHTTPRequestHandler):
    	def do_GET(self):
		print "un GET"
		self.conf = checkConf()
		tmpdir = self.conf.getValue("tmpdir")
		f = open(tmpdir+"/waypointeditor.html")
        	self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
		print "un GET"
                return

class newthread(Thread):
	def __init__(self):
        	self.server = HTTPServer(('localhost', 7988), MyHandler)
		Thread.__init__ ( self )

	def run(self):
		while 1==1:
        		#server.serve_forever()
			print "molaaaaa"
		print "Iniciamos3"

class WaypointEditor:
	def __init__(self, data_path = None, vbox = None):
		self.data_path = data_path
		self.conf = checkConf()
		self.extension = Extension()
		self.moz = gtkmozembed.MozEmbed()
                vbox.pack_start(self.moz, True, True)
		vbox.show_all()
		self.htmlfile = ""
		thread = newthread()
		thread.start()
		# server.socket.close()
	
	def drawMap(self):
		#points,levels = Points.encodePoints(pointlist)
		#points = points.replace("\\","\\\\")
	
		#htmlfile = self.conf.getValue("tmpdir")+"/index.html"
		self.createHtml()
		tmpdir = self.conf.getValue("tmpdir")
		htmlfile = tmpdir+"/waypointeditor.html"
        	self.moz.load_url("file://"+htmlfile)
		#	self.htmlfile = htmlfile
		#else:
		#	pass
	
	def createHtml(self):
		tmpdir = self.conf.getValue("tmpdir")
		filename = tmpdir+"/waypointeditor.html"
		
		content = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"  xmlns:v="urn:schemas-microsoft-com:vml">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
    <title>Google Maps JavaScript API Example</title>

    <script id="googleapiimport" src="http://maps.google.com/maps?file=api&amp;v=2"
            type="text/javascript"></script>
    <script type="text/javascript">


	lon = "40.71213418976525";
	lat = "-73.96785736083984";
	name = "waipoint";
	description = "Una descripcion mas a ver que hace";
	sym = "City";  

	waypoint1 = Array (lon,lat,name,description,sym);
	lon = "12.71213418976525";
	lat = "-7.96785736083984";
	name = "waipoint2";
	description = "Una descripcion cualquiera";
	sym = "City";  
	waypoint2 = Array (lon,lat,name,description,sym);
	waypointList = Array (waypoint1,waypoint2);
 

	is_addmode = 0;
    //<![CDATA[
	function createMarker(point, text) {
		//var icon = new GIcon();
		//icon.image = "./img.png";
		//icon.iconSize = new GSize(20, 34);
  		//var marker = new GMarker(point,icon);
  		var marker = new GMarker(point);
  		GEvent.addListener(marker, "click", function() {
    			marker.openInfoWindowHtml(text);
  			});
  		return marker;
		}

	function addWaypoint(lat,lon) {
		/*def getRecordInfo(self,id_record):*/
		var pytrainerAPI = new SOAPCall();
    		pytrainerAPI.transportURI = "http://localhost:7987/";


		var param1 = new SOAPParameter();
  		param1.name = "lat";
  		param1.value = lat;
 
		var param2 = new SOAPParameter();
  		param2.name = "lon";
  		param2.value = lon;
 
  		var parameters = [param1,param2];
		pytrainerAPI.encode(0,
                	"test", "namespaceURI",
                  	0, null,
                  	parameters.length, parameters);

		var response = pytrainerAPI.invoke();
    		if(response.fault){
    			  // error returned from the web service
      			//alert(response.fault.faultString);
			alert("mal");
    			} 
		else {
      			// we expect only one return SOAPParameter - the translated string.
			msg = response.getParameters(false, {});
  			alert("Return value: " + msg[0].value);
    			}
  		}  	


	function changeWaypoint(waypointslist) {
		w = waypointList[waypointslist.selectedIndex];
		lon = w[0];
		lat = w[1];
		map.panTo(new GLatLng(lon, lat));
		}
			

	function load() {
		if (GBrowserIsCompatible()) {
			map = new GMap2(document.getElementById("map"));
        		map.addControl(new GLargeMapControl());
        		map.addControl(new GMapTypeControl());
        		map.setCenter(new GLatLng(lon, lat), 11);

  		
			for (i=0; i<2; i++){
				lon = waypointList[i][0];
				lat = waypointList[i][1];
				name = waypointList[i][2];
				tag = "<b>"+waypointList[i][2]+"</b><br/>"+waypointList[i][3];
				point = new GLatLng(lon,lat);
  				map.addOverlay(createMarker(point, tag));
				myNewOption = new Option(name,i);
				document.theForm.waypointslist.options[i] = myNewOption;
				}
			GEvent.addListener(map, "click", function(marker, point) {
  				/*if (marker) {
    					map.removeOverlay(marker);
  				} else {*/
    				if (is_addmode==1){
					map.addOverlay(new GMarker(point));
					is_addmode = 0;
					addWaypoint(point.lat(),point.lng());
					}
				});
      			}
    		}	

	function addmode(){
		is_addmode = 1;
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
	<table >
	<tr><td width="100">
		<form name="theForm">
		<select size="25" style="width:150px" id="waypointslist" name="waypointslist" onchange="changeWaypoint(this.form.waypointslist)">
		</select>
		<input type="button" value="New Waipoint" style="width:150px" onclick="addmode();"/><br/>
		</form>
	</td><td>
    		<div id="map" style="width: 630px; height: 460px"></div>
	</td></tr>
	</table >
  </body>
</html>
"""
		file = fileUtils(filename,content)
		file.run()



