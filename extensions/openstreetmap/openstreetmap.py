#!/usr/bin/env python
from optparse import OptionParser
import os, stat
import sys
import logging
import gtk

import string
from lxml import etree

import httplib, httplib2
import urllib2
import mimetools, mimetypes
from json import dumps, loads       #   for deserializing JSON data form javascript

from pytrainer.extensions.mapviewer import MapViewer
from pytrainer.extensions.osm import Osm
from pytrainer.lib.localization import gtk_str

class openstreetmap:
    def __init__(self, parent = None, pytrainer_main = None, conf_dir = None, options = None):
        self.parent = parent
        self.pytrainer_main = pytrainer_main
        self.options = options
        self.conf_dir = conf_dir
        self.description = " "
        self.tags = ""
        self.visibility = "private"
        self.mozTitle=""               # Keeps embedded mozilla document title while displaying map for private area selection
        self.privBounds=[]             # Bounds of areas to be anonymized 

    def run(self, id, activity=None):  #TODO Convert to use activity...
        logging.debug(">>")
        try:
            uri = "http://api.openstreetmap.org/api/0.6/gpx/create" #URI for uploading traces to OSM
            if 'username' not in self.options or self.options['username'] == "" or 'password' not in self.options or self.options['password'] == "":
                logging.error("Must have username and password configured")
                raise Exception("Must have username and password configured")
            username = self.options['username']
            password = self.options['password']
            gpx_file = "%s/gpx/%s.gpx" % (self.conf_dir, id)
            if not os.path.isfile(gpx_file):
                raise Exception(str(gps_file) + ' File not found')
            #GPX file is ok and found, so open it
            logging.debug("GPX file: %s found, size: %d" % (gpx_file, os.path.getsize(gpx_file)))
            f = open(gpx_file, 'r')
            file_contents = f.read()
            #TODO Fix to use etree functionality.....
            if file_contents.find("<?xml version='1.0' encoding='ASCII'?>") != -1:
                logging.debug("GPX file: %s has ASCII encoding - updating to UTF-8 for OSM support" % gpx_file)
                f.close()                   #Close readonly file
                f = open(gpx_file, 'w')     #and open file for writing
                file_contents = file_contents.replace("<?xml version='1.0' encoding='ASCII'?>","<?xml version='1.0' encoding='UTF-8'?>", 1)
                f.write(file_contents)      #Write new content
                f.close()                   #Close
                f = open(gpx_file, 'r')     #Reopen in readonly mode
            #Get extra info from user
            response=self.display_options_window()
            if not response==gtk.RESPONSE_ACCEPT:
                f.close()
                logging.debug("User abort")
                return
            if self.makeanon:
                logging.debug("User requested anonymizing of GPX data")
                f.close()                   #Close standard gpxfile
                gpx_file = self.make_gpx_private(gpx_file)
                f = open(gpx_file, 'r')     #Open anonymous gpxfile in readonly mode
            fields = (("description",self.description), ("tags",self.tags), ("visibility",self.visibility))
            logging.debug("Added fields: %s" % str(fields))
            #Multipart encode the request
            boundary, body = self.multipart_encode(fields=fields, files=(("file", f),))
            content_type = 'multipart/form-data; boundary=%s' % boundary
            #Finished with the file so close it
            f.close()
            #Add the http headers to the request
            h = httplib2.Http()
            headers = {
                'Content-Type': content_type
            }
            #Add basic authentication credentials to the request
            h.add_credentials(username, password)
            #Show user something is happening
            msg = _("Posting GPX trace to Openstreetmap\n\nPlease wait this could take several minutes")
            md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_NONE, msg)
            md.set_title(_("Openstreetmap Extension Processing"))
            md.set_modal(True)
            md.show()
            while gtk.events_pending(): # This allows the GUI to update
                gtk.main_iteration()    # before completion of this entire action
            logging.debug("before request posting")
            #POST request to OSM
            res, content = h.request(uri, 'POST', body=body, headers=headers)
            logging.debug("after request posting")
            logging.debug("Got response status: %s, reason: %s, content: %s" % (res.status, res.reason, content))
            if res.reason == 'OK':
                res_msg = "Successfully posted to OSM.\nYou should get an email with the outcome of the upload soon\n\nTrace id is %s" % content
            else:
                res_msg = "Some error occured\nGot a status %s, reason %s\nContent was: %s" % (res.status, res.reason, content)
            #Close 'Please wait' dialog
            md.destroy()
            #Show the user the result
            md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, res_msg)
            md.set_title(_("Openstreetmap Extension Upload Complete"))
            md.set_modal(False)
            md.run()
            md.destroy()
        except Exception as e:
                msg = _("Error while uploading file to OSM: " + str(e))
                md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, msg)
                md.set_title(_("Openstreetmap Extension Error"))
                md.run()
                md.destroy()
                return
        finally:
            logging.debug("<<")

    def display_options_window(self):
        self.prefwindow = gtk.Dialog(title=_("Please add any additional information for this upload"), parent=None, flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, buttons=(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        self.prefwindow.set_modal(False)
        table = gtk.Table(1,3)
        self.entryList = []
        #Add description
        label = gtk.Label("<b>Description</b>")
        label.set_use_markup(True)
        entry = gtk.Entry()
        self.entryList.append(entry)
        table.attach(label,0,1,0,1)
        table.attach(entry,1,2,0,1)
        #Add tags
        label = gtk.Label("<b>Tags</b>")
        label.set_use_markup(True)
        entry = gtk.Entry()
        self.entryList.append(entry)
        table.attach(label,0,1,1,2)
        table.attach(entry,1,2,1,2)
        #Add visibility
        label = gtk.Label("<b>Visibility</b>")
        label.set_use_markup(True)
        combobox = gtk.combo_box_new_text()
        combobox.append_text("private")
        combobox.append_text("public")
        combobox.append_text("trackable")
        combobox.append_text("identifiable")
        combobox.set_active(0)
        table.attach(combobox,1,2,2,3)
        self.entryList.append(combobox)
        table.attach(label,0,1,2,3)
        #Add anonymize GPX option
        label = gtk.Label("<b>Anonymize GPX Data</b>")
        label.set_use_markup(True)
        table.attach(label,0,1,3,4)
        checkbutton = gtk.CheckButton()
        table.attach(checkbutton,1,2,3,4)
        self.entryList.append(checkbutton)
        #Add anon area selection button
        button = gtk.Button("Area selection")
        button.connect("clicked",self.areaSelect)
        table.attach(button,1,2,4,5)
        self.entryList.append(button)
        #Build dialog and show
        self.prefwindow.vbox.pack_start(table)
        self.prefwindow.show_all()
        self.prefwindow.connect("response", self.on_options_ok_clicked)
        response=self.prefwindow.run()
        self.prefwindow.destroy()
        return response

    def on_options_ok_clicked(self, widget, response_id):
        if not response_id == gtk.RESPONSE_ACCEPT:
            return response_id
        self.description = gtk_str(self.entryList[0].get_text())
        if self.description == "":
            logging.debug("A description is required - setting to default")
            self.description = "Uploaded from pytrainer"
        self.tags = gtk_str(self.entryList[1].get_text())
        self.visibility = gtk_str(self.entryList[2].get_active_text())
        self.makeanon = self.entryList[3].get_active()
        logging.debug("Description: %s, tags: %s, visibility: %s, makeanon: %s" % ( self.description, self.tags, self.visibility, self.makeanon) )

    def areaSelect(self,dc):
        """
            Open a window with OSM map so user could select his private/anonymized area - 
            all GPX dots in this area will be removed before uploading to OSM
        """       
        try:
            wTree = gtk.glade.XML(self.pytrainer_main.data_path+"extensions/openstreetmap/OSM_AnonSelection.glade")
            self.privAreaWindow = wTree.get_widget("OSM_AnonSelection")
            dic = {
                "on_buttonOk_clicked" : self.privArea_Ok,
                "on_buttonCancel_clicked" : self.privArea_Cancel
            }
            wTree.signal_autoconnect( dic )
            mapviewer = MapViewer(self.pytrainer_main.data_path, pytrainer_main=self.pytrainer_main, box=wTree.get_widget("mapBox"))
            json=None
            if self.options.has_key('privPolygon'):
                json=self.options['privPolygon']
            htmlfile = Osm(data_path=self.pytrainer_main.data_path, waypoint=json, pytrainer_main=self.pytrainer_main).selectArea()
            mapviewer.display_map(htmlfile=htmlfile)
            mapviewer.moz.connect('title', self.parseTitle) 
            self.privAreaWindow.show()

        except Exception as e:
                msg = "Could not init map selection screen, Error: " + str(e)
                md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, msg)
                md.set_title(_("Error"))
                md.run()
                md.destroy()
                return                

    def parseTitle(self, moz):
        "Event fired when document title was changed -> meaning polygon was changed"
        if moz.get_title() != "":
            self.mozTitle=str(moz.get_title())

    def privArea_Cancel(self,button):
        "Event fired when cancel button was pressed"
        self.privAreaWindow.destroy()
        
    def privArea_Ok(self,button):
        "Event fired when ok button was pressed"
        logging.debug(">> privArea_Ok")
        # save new private area polygon if changed
        if self.mozTitle=="":
            return
        # try parsing JSON
        try:
            # verify json is correct by deserializing and serializing it
            polygonString=dumps(loads(self.mozTitle))
            # try saving
            extensionDir = self.pytrainer_main.data_path + "/extensions" + "/openstreetmap"
            if not os.path.isdir(extensionDir):
                loggin.error(str(e))
                raise Exception("Could not find extension path: " + str(extensionDir))
            # save new options
            self.options['privPolygon'] = polygonString
            # convert dictionary to a lists set
            savedOptions = []
            for key in self.options:
                savedOptions.append((key,self.options[key]))
            # write new xml config file
            self.parent.setExtensionConfParams(extensionDir, savedOptions)
        except Exception as e:
            logging.error(str(e))    
            msg = _(str(e))
            md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, msg)
            md.set_title(_("Error while saving extension configuration"))
            md.run()
            md.destroy()
        finally:
            self.privAreaWindow.destroy()
                                
    def multipart_encode(self, fields, files, boundary = None, buffer = None):
        '''
            Multipart encode data for posting
             from examples at from http://odin.himinbi.org/MultipartPostHandler.py & http://bitworking.org/projects/httplib2/doc/html/libhttplib2.html
        '''
        if boundary is None:
            boundary = mimetools.choose_boundary()
        if buffer is None:
            buffer = ''
        for (key, value) in fields:
            buffer += '--%s\r\n' % boundary
            buffer += 'Content-Disposition: form-data; name="%s"' % key
            buffer += '\r\n\r\n' + value + '\r\n'
        for (key, fd) in files:
            file_size = os.fstat(fd.fileno())[stat.ST_SIZE]
            filename = os.path.basename(fd.name)
            contenttype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            buffer += '--%s\r\n' % boundary
            buffer += 'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename)
            buffer += 'Content-Type: %s\r\n' % contenttype
            # buffer += 'Content-Length: %s\r\n' % file_size
            fd.seek(0)
            buffer += '\r\n' + fd.read() + '\r\n'
        buffer += '--%s--\r\n\r\n' % boundary
        return boundary, buffer
        
    def make_gpx_private(self, gpx_file=None):
        '''
        wipes out private data from gpx files
        converts laps to waypoints
        '''
        logging.debug(">>")
        if gpx_file is None:
            return None
        
        filen = os.path.basename(gpx_file)
        tmpdir = self.pytrainer_main.profile.tmpdir
        anon_gpx_file = "%s/%s" % (tmpdir, filen)

        # get saved private area polygon
        pP=loads(self.options['privPolygon'])
        pP=pP['geometry']['coordinates'][0]
        # converts polygon's 2D matrix into a vector of just the lats or lons
        vector = lambda lonLat: [pP[i][lonLat] for i in range(len(pP))] # 0:lon, 1:lat
        # try reading private area's bounds, stored as [lon,lat]
        NE_LAT = max([pP[i][1] for i in range(len(pP))])
        NE_LON = max([pP[i][0] for i in range(len(pP))])
        SW_LAT = min([pP[i][1] for i in range(len(pP))])
        SW_LON = min([pP[i][0] for i in range(len(pP))])
        logging.info("Anonymizing Area: NE:%f,%f -> SW: %f,%f" % (NE_LON, NE_LAT, SW_LON, SW_LAT))
            
        # Config parameters, not used yet
        FILTER_BOX = True
        ERASE_TIME  = True
        LAP_TO_WAYPOINT = True

        tree = etree.parse(gpx_file)
        _xmlns = tree.getroot().nsmap[None]
        _trkpt_path = '{%s}trk/{%s}trkseg/{%s}trkpt' % (_xmlns, _xmlns, _xmlns)
        # namespace of gpx files
        NS = dict(ns='http://www.topografix.com/GPX/1/1')

        myroot =  tree.getroot()
        gpxdataNS = string.Template(\
            ".//{http://www.cluetrust.com/XML/GPXDATA/1/0}$tag")
        lapTag = gpxdataNS.substitute(tag="lap")
        endPointTag = gpxdataNS.substitute(tag="endPoint")
        triggerTag = gpxdataNS.substitute(tag="trigger")
        laps = tree.findall(lapTag)

        mygpx = tree.find('gpx')

        for lap in laps:
            trigger = lap.find(triggerTag)
            #  Watch out for manually triggered laps
            if trigger.text == 'manual':
                endPoint = lap.find(endPointTag)
                lat = endPoint.get("lat")
                lon = endPoint.get("lon")
                # Create waypt if not in home box
                try:
                    if not ((SW_LAT < float(lat) < NE_LAT) and (SW_LON < float(lon) < NE_LON)):
                        etree.SubElement(myroot, 'wpt', attrib= {'lat':lat, 'lon':lon})
                except:
                    pass
        etree.strip_attributes(myroot, 'creator')
                    
        # Wipe out home box
        for trkpt in tree.findall(_trkpt_path):
            lat = float(trkpt.attrib['lat'])
            lon = float(trkpt.attrib['lon'])
            if (lat < NE_LAT) & (lon < NE_LON) & (lat > SW_LAT) & (lon > SW_LON):
                par = trkpt.getparent()
                par.remove(trkpt)

        time = tree.xpath('//ns:trkpt/ns:time', namespaces=NS)
        for i in time:
            i.text = '1970-01-01T00:00:00+00:00'
            # osm regards <time> as mandatory. gnaa.

        ext = tree.xpath('//ns:gpx/ns:extensions', namespaces=NS)
        for i in ext:
            par = i.getparent()
            par.remove(i)
        meta = tree.xpath('//ns:gpx/ns:metadata', namespaces=NS)
        for i in meta:
            par = i.getparent()
            par.remove(i)
        ele = tree.xpath('//ns:trkpt/ns:ele', namespaces=NS)
        for i in ele:
            par = i.getparent()
            par.remove(i)

        # test schema on cleaned xml-tree
        # gpx.xsd from http://www.topografix.com/gpx.asp

        #xmlschema = etree.XMLSchema(etree.parse('gpx.xsd'))
        #xmlschema.validate(tree)

        # write new gpx file
        tree.write(anon_gpx_file, pretty_print=False, xml_declaration=True, encoding='UTF-8')
        logging.debug("<<")
        return anon_gpx_file

