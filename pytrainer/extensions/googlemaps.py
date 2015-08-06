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
import logging
import colorsys
import math
import traceback

import pytrainer.lib.points as Points
from pytrainer.lib.fileUtils import fileUtils
from pytrainer.lib.uc import UC

class Googlemaps:
    def __init__(self, data_path = None, waypoint = None, pytrainer_main=None):
        logging.debug(">>")
        self.data_path = data_path
        self.waypoint=waypoint
        self.pytrainer_main = pytrainer_main
        self.htmlfile = "%s/googlemaps.html" % (self.pytrainer_main.profile.tmpdir)
        self.uc = UC()
        logging.debug("<<")
        
    def colorLine(self, polyline, average, variance):
        stdev = math.sqrt(variance)
        for i in polyline:
            speed = i[1]
            speed = (speed - (average - 2*stdev))/(4*stdev)
            speed = min(max(speed,0), 1)
            rgb_tuple = colorsys.hsv_to_rgb(0.66-(speed*0.66), 1, 0.8)
            rgb_tuple = (rgb_tuple[0] * 255,rgb_tuple[1] * 255,rgb_tuple[2] * 255)
            i[2] = '#%02x%02x%02x' % rgb_tuple
            
    def colorLineAbs(self, polyline):
        for i in polyline:
            speed = i[1]
            if 0 <= speed < 7.5: #walk
                rgb_tuple = colorsys.hsv_to_rgb(0.66, 1, (speed/7.5)*0.6)
            elif 7.5 <= speed < 15: #jog-run
                speed = ((speed-7.5)/7.5)
                rgb_tuple = colorsys.hsv_to_rgb(0.66-speed*0.66, 1, 0.6+speed*0.2)
            elif 15 <= speed < 40: #cycle
                speed = ((speed-15)/25.0)
                rgb_tuple = colorsys.hsv_to_rgb(1-speed, 1, 0.8+speed*0.2)
            else: # fast cycle
                rgb_tuple = colorsys.hsv_to_rgb(0, 1, 1)
            
            rgb_tuple = (rgb_tuple[0] * 255,rgb_tuple[1] * 255,rgb_tuple[2] * 255)
            i[2] = '#%02x%02x%02x' % rgb_tuple
                

    def drawMap(self,activity, linetype):
        '''Draw google map
            create html file using Google API version3
            render using embedded Webkit
        '''
        logging.debug(">>")
        points = []
        levels = []
        pointlist = []
        polyline = []

        list_values = activity.tracks 
        # (accum distance, elevation, total duration, speed, lat, lon, bpm, cadence, corrected elevation)
        # (19.963867183986643, 7.34716797, 6488, 13.791899119294959, 43.53392358, -5.634736, 146, None, None)
        if list_values is not None and list_values != [] and len(list_values) > 0:
            minlat, minlon = float(list_values[0][4]),float(list_values[0][5])
            maxlat=minlat
            maxlon=minlon
            
            av_sum = 0
            variance_sum = 0
            n = 0
            #logging.debug("\n, ".join(map(str, list_values)))
            for i in list_values:
                if linetype==1:
                    if i[3] is not None:
                        val = i[3]
                    else:
                        val = 0
                        logging.error("No valid speed value for trackpoint: distance: %s | lat: %s | lon: %s" %(i[0],i[4],i[5]))
                elif linetype==2:
                	val = i[6] if i[6] else 0
                elif linetype==3:
                	val = i[7] if i[7]!=None else 1
                else:
                    val = 1
                    
                variance_sum += (val)**2
                av_sum += val
                n += 1
                
                lat, lon = float(i[4]), float(i[5])
                minlat = min(minlat, lat)
                maxlat = max(maxlat, lat)
                minlon = min(minlon, lon)
                maxlon = max(maxlon, lon)
                pointlist.append((lat,lon))
                polyline.append(["new google.maps.LatLng(%s, %s)" % (lat, lon), val, ""])
                
            av_speed = av_sum / float(n)
            variance = (variance_sum / float(n)) - av_speed**2
            variance = max(variance, 16)

            self.colorLine(polyline, av_speed, variance)
            #self.colorLineAbs(polyline)
            
            logging.debug("minlat: %s, maxlat: %s" % (minlat, maxlat))
            logging.debug("minlon: %s, maxlon: %s" % (minlon, maxlon))
            points,levels = Points.encodePoints(pointlist)
            points = points.replace("\\","\\\\")
            logging.debug("Using Google Maps version 3 API")
            laps = activity.laps
            timeHours = activity.duration / 3600
            timeMin = (float(activity.duration) / 3600.0 - timeHours) * 60
            time = "%d%s %02d%s" % (timeHours, _("h"), timeMin, _("min"))
            startinfo = "<div class='info_content'>%s: %s</div>" % (activity.sport_name, activity.title)
            finishinfo = "<div class='info_content'>%s: %s<br>%s: %s%s</div>" % (_("Time"), time, _("Distance"), activity.distance, self.uc.unit_distance)
            startinfo = startinfo.encode('ascii', 'xmlcharrefreplace') #Encode for html
            finishinfo = finishinfo.encode('ascii', 'xmlcharrefreplace') #Encode for html
            self.createHtml_api3(polyline, minlat, minlon, maxlat, maxlon, startinfo, finishinfo, laps, linetype)
        else:
            self.createErrorHtml()
        return self.htmlfile
        logging.debug("<<")

    def createHtml_api3(self,polyline, minlat, minlon, maxlat, maxlon, startinfo, finishinfo, laps, linetype):
        '''
        Generate a Google maps html file using the v3 api
            documentation at http://code.google.com/apis/maps/documentation/v3
        '''
        logging.debug(">>")
        if self.waypoint is not None:
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
        content += "            var startlatlng = %s ;\n" % (polyline[0][0])
        content += "            var centerlatlng = new google.maps.LatLng(%f, %f);\n" % ((minlat+maxlat)/2., (minlon+maxlon)/2.)
        content += "            var endlatlng = %s;\n" % (polyline[-1][0])
        content += "            var swlatlng = new google.maps.LatLng(%f, %f);\n" % (minlat,minlon)
        content += "            var nelatlng = new google.maps.LatLng(%f, %f);\n" % (maxlat,maxlon)
        content += "            var startcontent = \"%s\";\n" % (startinfo)
        content += "            var finishcontent = \"%s\";\n" % (finishinfo)
        content += "            var startimageloc = \"%s/glade/start.png\";\n" % (os.path.abspath(self.data_path))
        content += "            var finishimageloc = \"%s/glade/finish.png\";\n" % (os.path.abspath(self.data_path))
        content += "            var lapimageloc = \"%s/glade/waypoint.png\";\n" % (os.path.abspath(self.data_path))
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

        #"id_lap, record, elapsed_time, distance, start_lat, start_lon, end_lat, end_lon, calories, lap_number",
        for lap in laps:
            lapNumber = int(lap['lap_number'])+1
            elapsedTime = float(lap['elapsed_time'])
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
                lapLat = float(lap['end_lat'])
                lapLon = float(lap['end_lon'])
                content += "var lap%dmarker = new google.maps.Marker({position: new google.maps.LatLng(%f, %f), icon: lapimage, map: map,  title:\"Lap%d\"}); \n " % (lapNumber, lapLat, lapLon, lapNumber)
                content += "var lap%d = new google.maps.InfoWindow({content: \"<div class='info_content'>End of lap:%s<br>Elapsed time:%s<br>Distance:%0.2f km<br>Calories:%s</div>\" });\n" % (lapNumber, lapNumber, strElapsedTime, float(lap['distance'])/1000, lap['calories'])
                content += "google.maps.event.addListener(lap%dmarker, 'click', function() { lap%d.open(map,lap%dmarker); });\n" % (lapNumber,lapNumber,lapNumber)
            except Exception as e:
                #Error processing lap lat or lon
                #dont show this lap
                logging.debug( "Error processing lap "+ str(lap) )
                logging.debug(str(e))

        content += '''

            var boundsBox = new google.maps.LatLngBounds(swlatlng, nelatlng );\n
            map.fitBounds(boundsBox);\n'''
            
        pre = 0
        for point in polyline:
            if pre:
                content += '''var polylineCoordinates = [\n'''
                content += "                                       %s,\n" % (pre[0])
                content += "                                       %s,\n" % (point[0])
                content += '''            ];\n
                    // Add a polyline.\n
                    var polyline = new google.maps.Polyline({\n
                            path: polylineCoordinates,\n
                            strokeColor: \"%s\",\n
                            strokeOpacity: 0.9,\n
                            strokeWeight: 5,\n
                            });\n
                polyline.setMap(map);\n''' % point[2]
                
                contenttemplate = [
                	"%s",
                	"Speed: %0.1f km/h",
                	"HR: %d bpm",
                	"Cadence: %d",
                ]
                
                content += '''
                    google.maps.event.addListener(polyline, 'click', function(event) {
                        var marker = new google.maps.InfoWindow({
                          position: event.latLng, 
                          content: "%s"
                        });
                        marker.setMap(map);
                    });
                    ''' % contenttemplate[linetype] % point[1]
            pre = point
        
        content += '''
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

    def createErrorHtml(self):
        logging.debug(">>")
        content = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"  xmlns:v="urn:schemas-microsoft-com:vml">
<head>
</head>
<body>
No Gpx Data
</body>
</html>
        '''
        file = fileUtils(self.htmlfile,content)
        file.run()
        logging.debug("<<")
