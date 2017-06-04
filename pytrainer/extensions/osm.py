# Open Street Maps

# TODO: Add Google satellite images layers ?
# TODO: Create map class/interface that osm/googlemaps will inherit from ?

import os
import re
import logging
import urllib           # for downloading cached versions of openlayers.js and openstreetmaps.js
import time             # Used for checking if local cached file is current
    
from pytrainer.lib.gpx import Gpx
import pytrainer.lib.points as Points
from pytrainer.lib.fileUtils import fileUtils
from pytrainer.record import Record
from pytrainer.lib.uc import UC

class Osm:
    # Default URLS
    URLS = {'OpenLayers.js' : "http://openlayers.org/api/OpenLayers.js",
            'OpenStreetMap.js' : "http://www.openstreetmap.org/openlayers/OpenStreetMap.js"}
    # URLS that will not be cached
    staticURLS = {'OpenLayers' : 'http://openlayers.org/api/'}                 #openlayers default location

    def __init__(self, data_path = None, waypoint = None, pytrainer_main=None):
        logging.debug(">>")
        self.data_path = data_path
        self.waypoint = waypoint
        self.pytrainer_main = pytrainer_main
        self.tmpdir = (self.pytrainer_main.profile.tmpdir)
        self.htmlfile = "%s/osm.html" % (self.tmpdir)
        self.uc = UC()
        logging.debug("<<")

    def download(self,url,localfile):
        """Copy the contents of a file from a given URL to pytrainer's tmpdir
        """    
        logging.debug(">>")
        print "Downloading %s" % (url)
        webFile = urllib.urlopen(url)
        # always store downloaded files in tmpdir/cache
        localFile = open(self.tmpdir + '/cache/' + localfile, 'w')
        localFile.write(webFile.read())
        webFile.close()
        localFile.close()
        logging.debug("<<")
        
    def cacheUrls(self):
        ''' Store URL copies of needed files locally, 
            download new versions every ~14 days or if files does'nt exists
        '''
        #TODO: open a msg/progress bar while downloading the new files to inform the user
        logging.debug(">>")
        # create cache subfolder in tmpdir if not already there
        try:
            cachedir = self.tmpdir + '/cache';
            if not os.path.isdir(cachedir):
                print "Creating %s folder" % (cachedir)
                os.mkdir(cachedir)
                
            for localfile in self.URLS:
                # local cached file does not exists? download it
                if not os.path.isfile(cachedir + '/' + localfile):
                    self.download(self.URLS[localfile],localfile)
                else: 
                    creationTime = os.path.getctime(cachedir + '/' + localfile)     # read file creation time
                    if creationTime > time.time():                                  # file is in the future?! download it again
                        self.download(self.URLS[localfile],localfile)
                    elif creationTime + 14*24*60*60 < time.time():                  # 14 (days) * 24 hours * 60 minutes * 60 seconds = 14 days 
                        self.download(self.URLS[localfile],localfile)           
                # No exception was thrown, assuming local cache file exists and current
                self.URLS[localfile]='file://' + cachedir + '/' + localfile;
                logging.info("Using %s file " % (self.URLS[localfile]))
        except Exception as e:
            loggin.error("(%s) Error while downloading %s to local cache, using default hosted file instaed." \
                           % (str(e), self.URLS[localfile]))
        logging.debug("<<")
    
    def drawMap(self, activity, linetype):
        '''Draw OSM map
        create HTML file using Open Layers and Open Street Map
        render using embedded Webkit
        '''
        logging.debug(">>")
        points = []
        levels = []
        pointlist = []
        polyline = []
        attrlist = []

        try :
            list_values = activity.tracks
            if list_values is not None and list_values != [] and len(list_values) > 0:
                for i in list_values:
                    lat, lon = float(i[4]), float(i[5])
                    pointlist.append((lat,lon))
                    polyline.append("[%s, %s]" % (lon, lat))
                    attrlist.append((i[3],i[6])) # (Speed, HR)
                points,levels = Points.encodePoints(pointlist)
                points = points.replace("\\","\\\\")
                laps = activity.laps
                timeHours = int(activity.time) / 3600
                timeMin = (float(activity.time) / 3600.0 - timeHours) * 60
                time = "%d%s %02d%s" % (timeHours, _("h"), timeMin, _("min"))
                startinfo = "<div class='info_content'>%s: %s</div>" % (activity.sport_name, activity.title)
                finishinfo = "<div class='info_content'>%s: %s<br>%s: %s%s</div>" % (_("Time"), \
                            time, _("Distance"), activity.distance, self.uc.unit_distance)
                startinfo = startinfo.encode('ascii', 'xmlcharrefreplace') #Encode for html
                finishinfo = finishinfo.encode('ascii', 'xmlcharrefreplace') #Encode for html

                self.createHtml_osm(polyline, startinfo, finishinfo, laps, attrlist, linetype)
            else:
                self.createErrorHtml()
        except Exception as e:
            self.createErrorHtml(e)
        
        return self.htmlfile
        logging.debug("<<")

    def selectArea(self,dc=None):
    
        # try using local cached versions of JS files for faster rendering
        self.cacheUrls();

        content = '''
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
        <link rel="stylesheet" href="../theme/default/style.css" type="text/css" />
        <link rel="stylesheet" href="style.css" type="text/css" />
        <style type="text/css">
            p {
                width: 512px;
            }
            #config {
                margin-top: 1em;
                width: 512px;
                position: relative;
                height: 8em;
            }
            #controls {
                padding-left: 2em;
                margin-left: 0;
                width: 12em;
            }
            #controls li {
                padding-top: 0.5em;
                list-style: none;
            }
            #options {
                font-size: 1em;
                top: 0;
                margin-left: 15em;
                position: absolute;
            }

            /* avoid pink tiles */
            .olImageLoadError {
                background-color: transparent !important;
            }
        </style>

        <!-- Load libraries from remote or local cache -->
        <script src="''' + self.URLS['OpenLayers.js']    + '''"></script>
        <script src="''' + self.URLS['OpenStreetMap.js'] + '''"></script>

        <script type="text/javascript">
            var map, polygonControl;
            function init(){

                //"fix" locations
                OpenLayers.ImgPath="''' + self.staticURLS['OpenLayers'] + '''img/";
                OpenLayers.scriptLocation="''' + self.staticURLS['OpenLayers'] + '''";
                OpenLayers._getScriptLocation=function() { return "''' + self.staticURLS['OpenLayers'] + '''";};
                            
                // for transforming WGS 1984 to Spherical Mercator Projection
                pWGS = new OpenLayers.Projection("EPSG:4326");
                pMP = new OpenLayers.Projection("EPSG:900913");

                map = new OpenLayers.Map ("map", {
                    controls:[
                        new OpenLayers.Control.Navigation(),
                        new OpenLayers.Control.PanZoomBar(),
                        new OpenLayers.Control.LayerSwitcher(),
                        new OpenLayers.Control.Attribution(),
                        new OpenLayers.Control.MousePosition()],
                    maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
                    maxResolution: 156543.0399,
                    numZoomLevels: 19,
                    units: 'm',
                    projection: pMP,
                    displayProjection: pWGS
                } );

                //Add open street maps layers
                layerMapnik = new OpenLayers.Layer.OSM.Mapnik("Mapnik");
                map.addLayer(layerMapnik);

                //Add polygon drawing layer
                var polygonLayer = new OpenLayers.Layer.Vector("Polygon Layer");
                map.addLayer(polygonLayer);
                
                polyOptions = {sides: 4, irregular: true};
                polygonControl = new OpenLayers.Control.DrawFeature(polygonLayer,
                                                OpenLayers.Handler.RegularPolygon,
                                                {handlerOptions: polyOptions});

                // For desrializings
                var out_options = {
                    'internalProjection': map.baseLayer.projection,
                    'externalProjection': pWGS
                };

                // allow only one feature to be drawn
                polygonLayer.events.register("beforefeatureadded", polygonLayer, function(f) { polygonLayer.removeAllFeatures(true)});
                // Change title after draw
                polygonLayer.events.register("featureadded", polygonLayer, function(f) { 
                    var title=(new OpenLayers.Format.GeoJSON(out_options).write(f.feature,false));
                    document.title=title;
                    });
                
                //prepaint saved polygon
                savedPolygon = \'''' + str(self.waypoint) + '''\';
                if ((savedPolygon) && (savedPolygon!=='None')) {            
                   // deserialize 
                   var geojson_format = new OpenLayers.Format.GeoJSON(out_options);
                   var feature = geojson_format.read(savedPolygon);
                   // make sure it's an array
                   if(feature.constructor != Array)
                        feature = [feature];
                   if (feature && feature.length>0) {
                      var bounds = feature[0].geometry.getBounds();
                      polygonLayer.addFeatures(feature);
                      map.zoomToExtent(bounds);
                   }
                } else {
                    map.setCenter(new OpenLayers.LonLat(0, 0), 3);
                }         

                map.addControl(polygonControl);            
                
                document.getElementById('noneToggle').checked = true;
                
            }
            
            function setOptions(options) {
                polygonControl.handler.setOptions(options);
            }
            
            function setSize(fraction) {
                var radius = fraction * map.getExtent().getHeight();
                polygonControl.handler.setOptions({radius: radius,
                                                   angle: 0});
            }
        </script>
        </head>

          <body onload="init()">
            <input type="radio" name="type"
                   value="none" id="noneToggle"
                   onclick="polygonControl.deactivate()"
                   checked="checked" />
            <label for="noneToggle">Navigate</label>
            <input type="radio" name="type"
                   value="polygon" id="polygonToggle"
                   onclick="polygonControl.activate()" />
            <label for="polygonToggle">Draw polygon</label>
            <div id="map" class="smallmap"></div>   
          </body>
        </html>'''     

        file = fileUtils(self.htmlfile,content)
        file.run()
        return self.htmlfile
        
    def createHtml_osm(self, polyline, startinfo, finishinfo, laps, attrlist, linetype):
        '''
        Generate OSM map html file using MapLayers
        '''
        logging.debug(">>")

        # try using local cached versions of JS files for faster rendering
        self.cacheUrls();
        
        content = '''<html>
        <head>
            <!-- bring in the OpenLayers javascript library
                 (here we bring it from the remote site, but you could
                 easily serve up this javascript yourself) -->
            <script src="''' + self.URLS['OpenLayers.js'] + '''"></script>
            <!-- bring in the OpenStreetMap OpenLayers layers.
                 Using this hosted file will make sure we are kept up
                 to date with any necessary changes -->
            <script src="''' + self.URLS['OpenStreetMap.js'] + '''"></script>

            <script type="text/javascript">
                //complex object of type OpenLayers.Map
                var map;

                //icons data object
                var icons = {
                    iconSize : new OpenLayers.Size(30,30)'''

        # If have laps data insert markers here
        try:
            lapsContent=''
            for lap in laps[:500]:  # OpenLayers with firefox is limited to 500 markers -> TODO: Transfer to a constant somewhere ?
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
                lapLat = float(lap['end_lat'])
                lapLon = float(lap['end_lon'])
                #build laps content string
                lapsContent+=',\n'
                lapsContent+='\t\t\t\t\tlap%d: { url : "/waypoint.png", coordinates : [%f,%f], popupInfo: "%s" }' % \
                        (lapNumber, lapLon, lapLat, \
                        "<div class='info_content'>End of lap:%d<br>Elapsed time:%s<br>Distance:%0.2f km<br>Calories:%s</div>" % \
                            (lapNumber, strElapsedTime, float(lap['distance'])/1000, lap['calories'])
                        )
            content+=lapsContent
        except Exception as e:
            # If something breaks here just skip laps data
            logging.error('Error formating laps data: ' + str(e))
        # Insert start/finish track markers
        content+=''',\n        start : { url : "/start.png", coordinates : %s, popupInfo : "%s" },
                    finish : { url : "/finish.png", coordinates : %s, popupInfo : "%s" },
                    url : "file://%s/glade"''' \
                    % (polyline[0], startinfo, polyline[-1], finishinfo, os.path.abspath(self.data_path))

        content+='''};\n
                function init() {

                // fool openlayers scripts so it will download images and themes from the web instead of local folder if cached
                OpenLayers.ImgPath="''' + self.staticURLS['OpenLayers'] + '''img/";
                OpenLayers.scriptLocation="''' + self.staticURLS['OpenLayers'] + '''";
                OpenLayers._getScriptLocation=function() { return "''' + self.staticURLS['OpenLayers'] + '''";};

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
                            ['''
        #Insert track points here
        content+=",".join(polyline);
        content+=''']
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

    def createErrorHtml(self,errMsg=None):
        logging.debug(">>")
        errMsg = errMsg or ''       # convert None to empty string
        content = '''
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml"  xmlns:v="urn:schemas-microsoft-com:vml">
            <body>
            No GPX Data (''' + str(errMsg) + ''')
            </body>
        </html>
        '''
        file = fileUtils(self.htmlfile,content)
        file.run()
        logging.debug("<<")

