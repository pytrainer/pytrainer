# Testing OpenStreetMaps integration
# TODO: store OpenLayers.js locally (1MB file)
# TODO: Add start/finish/lap markers + info popups on click with full details

import gtkmozembed
import os
import re
import logging

from pytrainer.lib.gpx import Gpx
import pytrainer.lib.points as Points
from pytrainer.lib.fileUtils import fileUtils
from pytrainer.record import Record

class Osm:
	def __init__(self, data_path = None, waypoint = None, pytrainer_main=None):
		logging.debug(">>")
		self.data_path = data_path
		self.waypoint=waypoint
		self.pytrainer_main = pytrainer_main
		self.htmlfile = "%s/osm.html" % (self.pytrainer_main.profile.tmpdir)
		logging.debug("<<")

	def drawMap(self,activity):
		'''Draw osm map
			create html file using Open Layers and Open Street Map
			render using embedded Mozilla

			info at http://www.pygtk.org/pygtkmozembed/class-gtkmozembed.html
		'''
		logging.debug(">>")
		points = []
		levels = []
		pointlist = []
		polyline = []

		list_values = activity.tracks
		if list_values != []:
			if len(list_values) > 0:
				for i in list_values:
					lat, lon = float(i[4]), float(i[5])
					pointlist.append((lat,lon))
					polyline.append("[%s, %s]" % (lon, lat))
				points,levels = Points.encodePoints(pointlist)
				points = points.replace("\\","\\\\")
				laps = activity.laps
				timeHours = int(activity.time) / 3600
				timeMin = (float(activity.time) / 3600.0 - timeHours) * 60
				time = "%d%s %02d%s" % (timeHours, _("h"), timeMin, _("min"))
				startinfo = "<div class='info_content'>%s: %s</div>" % (activity.sport_name, activity.title)
				finishinfo = "<div class='info_content'>%s: %s<br>%s: %s%s</div>" % (_("Time"), time, _("Distance"), activity.distance, activity.distance_unit)
				startinfo = startinfo.encode('ascii', 'xmlcharrefreplace') #Encode for html
				finishinfo = finishinfo.encode('ascii', 'xmlcharrefreplace') #Encode for html

				self.createHtml_osm(polyline, startinfo, finishinfo, laps)
			else:
				self.createErrorHtml()
		else:
			self.createErrorHtml()
		#self.moz.load_url("file://%s" % (self.htmlfile))
		return self.htmlfile
		logging.debug("<<")

	def createHtml_osm(self, polyline, startinfo, finishinfo, laps):
		'''
		Generate OSM map html file using MapLayers
		'''
		logging.debug(">> OSM start createHtml")
		content = '''
		<html>
		<head>
			<!-- bring in the OpenLayers javascript library
				 (here we bring it from the remote site, but you could
				 easily serve up this javascript yourself) -->
			<script src="http://www.openlayers.org/api/OpenLayers.js"></script>
			<!-- bring in the OpenStreetMap OpenLayers layers.
				 Using this hosted file will make sure we are kept up
				 to date with any necessary changes -->
			<script src="http://www.openstreetmap.org/openlayers/OpenStreetMap.js"></script>

			<script type="text/javascript">
				//complex object of type OpenLayers.Map
				var map;

				//icons data object
				var icons = {
					start : { url : "/start.png", coordinates : %s, popupInfo : "%s" },
					finish : { url : "/finish.png", coordinates : %s, popupInfo : "%s" },
					lap : { url : "/lap.png" },
					url : "file://%s/glade",
				 	iconSize : new OpenLayers.Size(30,30)
					};''' % (polyline[0], startinfo, polyline[-1], finishinfo, os.path.abspath(self.data_path))
		content+='''\n
				function init() {

				// for transforming WGS 1984 to Spherical Mercator Projection
				pWGS = new OpenLayers.Projection("EPSG:4326");
				pMP = new OpenLayers.Projection("EPSG:900913");

				map = new OpenLayers.Map ("map", {
					controls:[
						new OpenLayers.Control.Navigation(),
						new OpenLayers.Control.PanZoomBar(),
						new OpenLayers.Control.LayerSwitcher(),
						new OpenLayers.Control.Attribution()],
					maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
					maxResolution: 156543.0399,
					numZoomLevels: 19,
					units: 'm',
					projection: pMP,
					displayProjection: pWGS
				} );

				// Track painting style
				var trackStyle = {
					strokeColor: "#33DDDD",
					strokeWidth: 3,
					strokeDashstyle: "solid",
					strokeOpacity: 0.6,
					pointRadius: 6,
				};

				//Build track object
				var track =
					{
					"type":"Feature",
					"id":"OpenLayers.Feature.Vector_259",
					"properties":{},
					"geometry":
					{
						"type":"LineString",
						"coordinates":
							[\n'''
		#Insert track points - all but last one
		for point in polyline[:-1]:
			content+="%s," % (point)
		#Insert last point without comma so the javascript syntax stays correct
		content+="%s\n" % (polyline[-1])
		content+='''				]
					},
					"crs":
						{
						"type":"OGC",
						"properties":
							{
							"urn":"urn:ogc:def:crs:OGC:1.3:CRS84"
							}
						}
					}

				//Add open street maps layers
				layerMapnik = new OpenLayers.Layer.OSM.Mapnik("Mapnik");
				map.addLayer(layerMapnik);
				layerTilesAtHome = new OpenLayers.Layer.OSM.Osmarender("Osmarender");
				map.addLayer(layerTilesAtHome);

				//Create vector layer to add the data on to
				var vector_layer = new OpenLayers.Layer.Vector();
				vector_layer.setName('Track');

				var geojson_format = new OpenLayers.Format.GeoJSON();
				var feature = geojson_format.read(track,"Feature");

				// transform from WGS 1984 to Spherical Mercator Projection
				feature.geometry.transform(pWGS, pMP);

				feature.geometry.calculateBounds();
				var vector=new OpenLayers.Feature.Vector();
				vector.geometry = feature.geometry;
				vector.style=trackStyle;

				vector_layer.addFeatures(vector);
				map.addLayer(vector_layer);

				// Insert start/finish markers
				layerMarkers = new OpenLayers.Layer.Markers("Markers");
				var offset = new OpenLayers.Pixel(-(icons.iconSize.w/2), -icons.iconSize.h);
				for (var i in icons) {
					if (icons[i].coordinates) {
						icons[i].icon = new OpenLayers.Icon(icons.url + icons[i].url,icons.iconSize,offset);
						icons[i].lonLat = new OpenLayers.LonLat(icons[i].coordinates[0],icons[i].coordinates[1]);
						icons[i].lonLat.transform(pWGS,pMP);
						icons[i].marker = new OpenLayers.Marker(icons[i].lonLat,icons[i].icon);
						icons[i].popup = new OpenLayers.Popup.FramedCloud("Info",
											icons[i].lonLat,
								                      	null,
										        icons[i].popupInfo,
											icons[i].icon,
										        true,
											null
											);
						icons[i].onClick = function(e) { map.addPopup(this.popup); this.popup.show(); }
						icons[i].marker.events.register("mousedown", icons[i], function(e) { this.onClick(e)} )
						layerMarkers.addMarker(icons[i].marker);
					}
				}
				map.addLayer(layerMarkers);

				//zoom and center to the track layouts
				map.zoomToExtent(feature.geometry.getBounds());

       		}
		</script>

		</head>
		<!-- body.onload is called once the page is loaded (call the 'init' function) -->
		<body onload="init();">
			<!-- define a DIV into which the map will appear. Make it take up the whole window -->
			<div style="width:100%; height:100%" id="map"></div>
		</body>
		</html>
		'''
		file = fileUtils(self.htmlfile,content)
		file.run()
		logging.debug("<<")

	def createErrorHtml(self):
		logging.debug(">>")
		content = '''
	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
	<html xmlns="http://www.w3.org/1999/xhtml"  xmlns:v="urn:schemas-microsoft-com:vml">
		<body>
		No Gpx Data
		</body>
	</html>
		'''
		file = fileUtils(self.htmlfile,content)
		file.run()
		logging.debug("<<")

