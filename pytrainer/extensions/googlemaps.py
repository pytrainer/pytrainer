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
import logging

from pytrainer.lib.system import checkConf
from pytrainer.lib.gpx import Gpx
import pytrainer.lib.points as Points 
from pytrainer.lib.fileUtils import fileUtils
from pytrainer.record import Record

class Googlemaps:
	def __init__(self, data_path = None, vbox = None, waypoint = None, useGM3 = False):
		logging.debug(">>")
		self.data_path = data_path
		self.conf = checkConf()
		gtkmozembed.set_profile_path("/tmp", "foobar") # http://faq.pygtk.org/index.py?req=show&file=faq19.018.htp
		self.moz = gtkmozembed.MozEmbed()
		vbox.pack_start(self.moz, True, True)
		vbox.show_all()
		self.htmlfile = "%s/index.html" % (self.conf.getValue("tmpdir")) 
		self.waypoint=waypoint
		self.useGM3 = useGM3
		self.record = Record()
		logging.debug("<<")
	
	def drawMap(self,id_record):
		'''Draw google map 
			create html file using Google API version??
			render using embedded Mozilla

			info at http://www.pygtk.org/pygtkmozembed/class-gtkmozembed.html
		'''
		logging.debug(">>")
		code = "googlemapsviewer"
		extensiondir = self.conf.getValue("extensiondir")+"/"+code
		if not os.path.isdir(extensiondir):
            		os.mkdir(extensiondir)
		points = []
		levels = []
		pointlist = []
		polyline = []
		
		gpxfile = "%s/%s.gpx" % (self.conf.getValue("gpxdir"), id_record)
		if os.path.isfile(gpxfile):
			gpx = Gpx(self.data_path,gpxfile)
			list_values = gpx.getTrackList()
			if len(list_values) > 0:
				minlat, minlon = float(list_values[0][4]),float(list_values[0][5])
				maxlat=minlat
				maxlon=minlon
				for i in list_values:
					lat, lon = float(i[4]), float(i[5])
					minlat = min(minlat, lat)
					maxlat = max(maxlat, lat)
					minlon = min(minlon, lon)
					maxlon = max(maxlon, lon)
					pointlist.append((lat,lon))
					polyline.append("new google.maps.LatLng(%s, %s)" % (lat, lon))
				logging.debug("minlat: %s, maxlat: %s" % (minlat, maxlat))
				logging.debug("minlon: %s, maxlon: %s" % (minlon, maxlon))
				points,levels = Points.encodePoints(pointlist)
				points = points.replace("\\","\\\\")
				if self.useGM3:
					logging.debug("Using Google Maps version 3 API")
					#laps = gpx.getLaps() # [](elapsedTime, lat, lon, calories, distance)
					#"id_lap, record, elapsed_time, distance, start_lat, start_lon, end_lat, end_lon, calories",  
					laps = self.record.getLaps(id_record)
					#"sports.name,date,distance,time,beats,comments,average,calories,id_record,title,upositive,unegative,maxspeed,maxpace,pace,maxbeats"
					info = self.record.getrecordInfo(id_record)
					timeHours = int(info[0][3]) / 3600
					timeMin = (float(info[0][3]) / 3600.0 - timeHours) * 60
					time = "%d%s %02d%s" % (timeHours, _("h"), timeMin, _("min"))
					startinfo = "<div class='info_content'>%s: %s</div>" % (info[0][0], info[0][9])
					finishinfo = "<div class='info_content'>%s: %s<br>%s: %s%s</div>" % (_("Time"), time, _("Distance"), info[0][2], _("km"))
					startinfo = startinfo.encode('ascii', 'xmlcharrefreplace') #Encode for html
					finishinfo = finishinfo.encode('ascii', 'xmlcharrefreplace') #Encode for html
					self.createHtml_api3(polyline, minlat, minlon, maxlat, maxlon, startinfo, finishinfo, laps)
				else:
					logging.debug("Using Google Maps version 2 API")
					self.createHtml(points,levels,pointlist[0])
			else:
				self.createErrorHtml()
		else:
			self.createErrorHtml()
		self.moz.load_url("file://%s" % (self.htmlfile))
		logging.debug("<<")
	
	def createHtml_api3(self,polyline, minlat, minlon, maxlat, maxlon, startinfo, finishinfo, laps):
		'''
		Generate a Google maps html file using the v3 api 
			documentation at http://code.google.com/apis/maps/documentation/v3
		'''
		logging.debug(">>")
		waypoints = self.waypoint.getAllWaypoints()
		#TODO waypoints not supported in this function yet
		#TODO sort polyline encoding (not supported in v3?)
		#TODO check http://code.google.com/apis/maps/documentation/v3/overlays.html#Polylines for MVArray??
		content = '''
		<html>
		<head>
		<style type="text/css">
			div.info_content { font-family: sans-serif; font-size: 10px; }
		</style>
		<meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
		<script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>
		<script type="text/javascript">
		  function initialize() {\n'''
		content += "		    var startlatlng = %s ;\n" % (polyline[0])
		content += "		    var centerlatlng = new google.maps.LatLng(%f, %f);\n" % ((minlat+maxlat)/2., (minlon+maxlon)/2.)
		content += "		    var endlatlng = %s;\n" % (polyline[-1])
		content += "		    var swlatlng = new google.maps.LatLng(%f, %f);\n" % (minlat,minlon)
		content += "		    var nelatlng = new google.maps.LatLng(%f, %f);\n" % (maxlat,maxlon)
		content += "		    var startcontent = \"%s\";\n" % (startinfo)
		content += "		    var finishcontent = \"%s\";\n" % (finishinfo)
		content += "		    var startimageloc = \"%s/glade/start.png\";\n" % (os.path.abspath(self.data_path))
		content += "		    var finishimageloc = \"%s/glade/finish.png\";\n" % (os.path.abspath(self.data_path))
		content += "		    var lapimageloc = \"%s/glade/waypoint.png\";\n" % (os.path.abspath(self.data_path))
		content +='''
		    var myOptions = {
		      zoom: 8,
		      center: centerlatlng,
			  scaleControl: true,
		      mapTypeId: google.maps.MapTypeId.ROADMAP
		    };

		    var startimage = new google.maps.MarkerImage(startimageloc,\n
		      // This marker is 32 pixels wide by 32 pixels tall.
		      new google.maps.Size(32, 32),
		      // The origin for this image is 0,0.
		      new google.maps.Point(0,0),
		      // The anchor for this image is the base of the flagpole
		      new google.maps.Point(16, 32));\n\n
		    var finishimage = new google.maps.MarkerImage(finishimageloc,\n
		      // This marker is 32 pixels wide by 32 pixels tall.
		      new google.maps.Size(32, 32),
		      // The origin for this image is 0,0.
		      new google.maps.Point(0,0),
		      // The anchor for this image is the base of the flagpole
		      new google.maps.Point(16, 32));\n

		    var lapimage = new google.maps.MarkerImage(lapimageloc,\n
		      // This marker is 32 pixels wide by 32 pixels tall.
		      new google.maps.Size(32, 32),
		      // The origin for this image is 0,0.
		      new google.maps.Point(0,0),
		      // The anchor for this image is the base of the flagpole
		      new google.maps.Point(16, 32));\n

		    var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
			var startmarker = new google.maps.Marker({
		      position: startlatlng, 
		      map: map, 
			  icon: startimage, 
		      title:"Start"}); 

			var finishmarker = new google.maps.Marker({
		      position: endlatlng, 
			  icon: finishimage, 
		      map: map, 
		      title:"End"}); \n

			//Add an infowindows
			var startinfo = new google.maps.InfoWindow({
			    content: startcontent
			});

			var finishinfo = new google.maps.InfoWindow({
			    content: finishcontent
			});

			google.maps.event.addListener(startmarker, 'click', function() {
			  startinfo.open(map,startmarker);
			});

			google.maps.event.addListener(finishmarker, 'click', function() {
			  finishinfo.open(map,finishmarker);
			});\n'''

		#"id_lap, record, elapsed_time, distance, start_lat, start_lon, end_lat, end_lon, calories",  
		for lap in laps:
			lapNumber = laps.index(lap)+1
			elapsedTime = float(lap[2])
			elapsedTimeHours = int(elapsedTime/3600)
			elapsedTimeMins = int((elapsedTime - (elapsedTimeHours * 3600)) / 60)
			elapsedTimeSecs = elapsedTime - (elapsedTimeHours * 3600) - (elapsedTimeMins * 60)
			if elapsedTimeHours > 0:
				strElapsedTime = "%0.0dh:%0.2dm:%0.2fs" % (elapsedTimeHours, elapsedTimeMins, elapsedTimeSecs) 
			elif elapsedTimeMins > 0:
				strElapsedTime = "%0.0dm:%0.2fs" % (elapsedTimeMins, elapsedTimeSecs) 
			else:
				strElapsedTime = "%0.0fs" % (elapsedTimeSecs) 
			#process lat and lon for this lap
			try:
				lapLat = float(lap[6])
				lapLon = float(lap[7])
				content += "var lap%dmarker = new google.maps.Marker({position: new google.maps.LatLng(%f, %f), icon: lapimage, map: map,  title:\"Lap%d\"}); \n " % (lapNumber, lapLat, lapLon, lapNumber)
				content += "var lap%d = new google.maps.InfoWindow({content: \"<div class='info_content'>End of lap:%s<br>Elapsed time:%s<br>Distance:%0.2f km<br>Calories:%s</div>\" });\n" % (lapNumber, lapNumber, strElapsedTime, float(lap[3])/1000, lap[8])
				content += "google.maps.event.addListener(lap%dmarker, 'click', function() { lap%d.open(map,lap%dmarker); });\n" % (lapNumber,lapNumber,lapNumber)
			except:
				#Error processing lap lat or lon
				#dont show this lap
				print "Error processing lap "+ str(lapNumber) + " id: " + lap(lap[0]) + " (lat,lon) ( " + str(lap[6]) + "," +str (lap[7]) + ")"

		content += '''

			var boundsBox = new google.maps.LatLngBounds(swlatlng, nelatlng );\n
			map.fitBounds(boundsBox);\n
			var polylineCoordinates = [\n'''
		for point in polyline:
			content += "			                           %s,\n" % (point)
		content += '''			  ];\n
			// Add a polyline.\n
			var polyline = new google.maps.Polyline({\n
					path: polylineCoordinates,\n
					strokeColor: \"#3333cc\",\n
					strokeOpacity: 0.6,\n
					strokeWeight: 5,\n
					});\n
			polyline.setMap(map);\n
		  }

		</script>
		</head>
		<body onload="initialize()">
		  <div id="map_canvas" style="width:100%; height:100%"></div>
		</body>
		</html>'''
		file = fileUtils(self.htmlfile,content)
		file.run()
		logging.debug("<<")

	def createHtml(self,points,levels,init_point):
		logging.debug(">>")
		waypoints = self.waypoint.getAllWaypoints()
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
		file = fileUtils(self.htmlfile,content)
		file.run()
		logging.debug("<<")
		
	def createErrorHtml(self):
		logging.debug(">>")
		content = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"  xmlns:v="urn:schemas-microsoft-com:vml">
<head>
<body>
No Gpx Data
</body>
</html>
		'''
		file = fileUtils(self.htmlfile,content)
		file.run()
		logging.debug("<<")
