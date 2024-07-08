# -*- coding: utf-8 -*-

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

from pytrainer.extension import Extension
from pytrainer.lib.fileUtils import fileUtils
from gi.repository import Gtk
import logging
import os
import re
from gi.repository import WebKit2

class WaypointEditor:
    def __init__(self, data_path = None, vbox = None, waypoint=None, parent=None):
        logging.debug(">>")
        self.data_path = data_path
        self.extension = Extension()
        self.wkview = WebKit2.WebView()
        self.wkview.connect('notify::title', self.handle_title_changed)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self.wkview)
        vbox.pack_start(scrolled_window, True, True, 0)
        vbox.show_all()
        self.htmlfile = ""
        self.waypoint=waypoint
        self.pytrainer_main=parent
        logging.debug("<<")

    def handle_title_changed(self, *args):
        title = self.wkview.get_title()
        if title == None:
            return
        logging.debug("Received title: "+ title)
        m = re.match("call:([a-zA-Z]*)[(](.*)[)]", title)
        if m:
            fname = m.group(1)
            args = m.group(2)
            if fname == "addWaypoint":
                am = re.match("([+-]?[0-9]+[.][0-9]+),([+-]?[0-9]+[.][0-9]+)", args)
                if am:
                    lon, lat = am.group(1), am.group(2)
                    lon, lat = float(lon), float(lat)
                    id_waypoint = self.waypoint.addWaypoint(lon, lat, "NEW WAYPOINT")
                    self.pytrainer_main.refreshWaypointView(default_waypoint=id_waypoint)
                else:
                    raise ValueError("Error parsing addWaypoint parameters: %s" % args)
            elif fname == "updateWaypoint":
                am = re.match("([+-]?[0-9]+[.][0-9]+),([+-]?[0-9]+[.][0-9]+),([0-9]*)", args)
                if am:
                    lon, lat, id_waypoint = am.group(1), am.group(2), am.group(3)
                    try:
                        lon, lat, id_waypoint = float(lon), float(lat), int(id_waypoint)
                    except ValueError as e:
                        logging.error("Error parsing addWaypoint parameters: %s %s", args, e)
                    retorno = self.waypoint.getwaypointInfo(id_waypoint)
                    if retorno:
                        name, comment, sym = retorno[0][5], retorno[0][3], retorno[0][6]
                        self.waypoint.updateWaypoint(id_waypoint, lat, lon, name, comment, sym)
                        self.pytrainer_main.refreshWaypointView(default_waypoint=id_waypoint)
                    else:
                        raise KeyError("Unknown waypoint id %d", id_waypoint)
                else:
                    raise ValueError("Error parsing addWaypoint parameters: %s" % args)
            else:
                raise ValueError("Unexpected function name %s" % fname)
        return False

    def drawMap(self):
        logging.debug(">>")
        #self.createHtml()
        tmpdir = self.pytrainer_main.profile.tmpdir
        htmlfile = tmpdir+"/waypointeditor.html"
        logging.debug("HTML file: "+str(htmlfile))
        self.wkview.load_uri("file://"+htmlfile)
        logging.debug("<<")

    def createHtml(self,default_waypoint=None):
        logging.debug(">>")
        tmpdir = self.pytrainer_main.profile.tmpdir
        filename = tmpdir+"/waypointeditor.html"

        points = self.waypoint.getAllWaypoints()
        londef = 0
        latdef = 0
        content = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml">
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8"/>
<title>edit waypoints</title>

<!-- Include Leaflet.js library -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<!-- Include Leaflet.Fullscreen plugin -->
<link rel="stylesheet" href="https://unpkg.com/leaflet.fullscreen@1.6.0/Control.FullScreen.css" />
<script src="https://unpkg.com/leaflet.fullscreen@1.6.0/Control.FullScreen.js"></script>

<script type="text/javascript">
//<![CDATA[
"""
        i = 0
        arrayjs = ""
        if default_waypoint is None and points:
            default_waypoint = points[0][0]
        for point in points:
            if point[0] == default_waypoint:
                londef = point[2]
                latdef = point[1]
            content += 'lon = "%f";\n'%point[2]
            content += 'lat = "%f";\n'%point[1]
            content += 'name = "%s";\n'%point[6]
            content += 'description = "%s";\n'%point[4]
            content += 'sym = "%s";\n'%point[7]
            content += 'id = "%d";\n'%point[0]
            content += """waypoint%d = Array (lon,lat,name,description,sym,id);\n"""%i
            if i>0:
                arrayjs+=","
            arrayjs +="waypoint%d"%i
            i = i+1
        content += """waypointList = Array (%s);\n""" %arrayjs
        content += """
is_addmode = 0;
var map;

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

    var point = [lat, lon];
    var text = "<b>" + waypoint[2] + "</b><br/>" + waypoint[3];

    var iconUrl = sym == "Summit" ? "/usr/local/python/3.12.0/share/pytrainer/glade/summit.png" : "/usr/local/python/3.12.0/share/pytrainer/glade/waypoint.png";
    var icon = L.icon({
        iconUrl: iconUrl,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
    });

    var marker = L.marker(point, {icon: icon, draggable: true}).addTo(map);
    marker.bindPopup(text);

    marker.on('dragend', function(event) {
        var position = event.target.getLatLng();
        updateWaypoint(position.lng, position.lat, id);
    });

    return marker;
}

function load() {
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
    map = L.map('map_canvas').setView([lat, lon], 11);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19
    }).addTo(map);

    L.control.fullscreen().addTo(map);

    for (var i = 0; i < waypointList.length; i++) {
        createMarker(waypointList[i]);
    }

    map.on('click', function(event) {
        if (is_addmode == 1) {
            var lon = event.latlng.lng;
            var lat = event.latlng.lat;

            var waypoint_id = addWaypoint(lon, lat);
            var waypoint = [lon, lat, "", "", "", waypoint_id];
            createMarker(waypoint);
            is_addmode = 0;
        }
    });
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

#addButton {
    position: absolute;
    top: 32px;
    left: 86px;
    z-index: 1000; /* Ensure the button is above the map */
}
</style>

</head>
<body onload="load()" style="cursor:crosshair">
    <div id="map_canvas" style="width: 100%; height: 460px; top: 0px; left: 0px;"></div>
    <div id="addButton">
        <input type="button" value="New Waypoint" onclick="javascript:addmode();" />
    </div>
</body>
</html>
"""
        file = fileUtils(filename,content)
        file.run()
        logging.debug("<<")
