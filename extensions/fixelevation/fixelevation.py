#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "jblance"
__contributors__ = "siggi, dgranda"
import os
import shutil
import gtk
import traceback
import logging
from lxml import etree
from pytrainer.lib.srtmlayer import SrtmLayer

class fixelevation:
    _data = None
    _srtm = SrtmLayer()

    def __init__(self, parent = None, pytrainer_main = None, conf_dir = None, options = None):
        self.parent = parent
        self.pytrainer_main = pytrainer_main
        self.options = options
        self.conf_dir = conf_dir

    def run(self, aid, activity=None):  #TODO Convert to use activity...
        logging.debug(">>")
        gpx_file = "%s/gpx/%s.gpx" % (self.conf_dir, aid)
        ele_fixed = True
        
        if os.path.isfile(gpx_file):
            logging.info("ELE GPX file: %s found, size: %d" % (gpx_file, os.path.getsize(gpx_file)))
            # Backup original raw data as *.orig.gpx
            backup_file(gpx_file)
            # Parse GPX file to ElementTree instance
            self.parse_gpx(gpx_file)
            trackpoints = self._data.findall(self._trkpt_path)
            if trackpoints:
                # Replace elevation from GPX+ by data from SRTM
                ele_fixed = self.replace_elevation(trackpoints)
                    
                if not ele_fixed:
                    # Try Google maps elevation API
                    import cjson, urllib2, math
                    steps = len(trackpoints) / 300

                    path = ''
                    lat_prev, long_prev = 0, 0
                    t = 0
                    for t in xrange(0,len(trackpoints),steps):
                        lat = float(trackpoints[t].attrib['lat'])
                        lon = float(trackpoints[t].attrib['lon'])
                        encoded_lat, lat_prev = encode_coord(lat, lat_prev)
                        encoded_long, long_prev = encode_coord(lon, long_prev)
                        path += encoded_lat + encoded_long
                        t += 1
                    url = "http://maps.googleapis.com/maps/api/elevation/json?sensor=true&samples=%d&path=enc:" % int((len(trackpoints) / steps))
                    url += path
     
                    try:
                        google_ele = cjson.decode(urllib2.urlopen(url).read())
                        if google_ele['status'] == "OK":
                            t_idx = 0
                            ele_points = len(google_ele['results'])
                            for ele_new in xrange(0,ele_points):
                                addExt(trackpoints[t_idx], google_ele['results'][ele_new]['elevation'])
                                for intermediate in xrange(ele_new+1, ele_new+steps):
                                    if intermediate<len(trackpoints):
                                        if ele_new==ele_points-1:
                                            calculated = google_ele['results'][ele_new]['elevation']
                                        else:
                                            ele1 = google_ele['results'][ele_new]['elevation']
                                            ele2 = google_ele['results'][ele_new+1]['elevation']
                                            calculated = (ele1 * (intermediate-ele_new)  + ele2 * (steps - (intermediate-ele_new))) / steps
                                        t_idx += 1
                                        addExt(trackpoints[t_idx], calculated)
                                t_idx += 1
                            ele_fixed = True
                    except urllib2.HTTPError:
                        logging.error("Error when trying to correct elevation using Google Maps Elevation service")
                        traceback.print_exc()
                        pass

                if ele_fixed:
                    # Write out to original *.gpx.                         
                    self._data.write(gpx_file, 
                                    encoding=self._data.docinfo.encoding, 
                                    xml_declaration=True, 
                                    pretty_print=False)
                    res_msg = _("Elevation has been fixed")
                    #TODO calculate ascent and descent values -> update DB (create new method in record class)
                    #TODO Expire activity out of pool - so get updated info
                    self.pytrainer_main.activitypool.remove_activity(aid)
                    #TODO reload gpx data in main window
                else:
                    res_msg = _("Elevation could not be fixed!")                 
            else:
                logging.error("Not able to find valid trackpoints in %s, nothing to correct" %gpx_file)
                res_msg = _("Elevation could not be fixed!")
        else:
            logging.error("ELE GPX file: %s NOT found!!!" % (gpx_file))
            res_msg = _("Elevation could not be fixed!")

        #Show the user the result
        md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, res_msg)
        md.set_title(_("Elevation Correction Complete"))
        md.set_modal(False)
        md.run()
        md.destroy()

        logging.debug("<<")

    def parse_gpx(self, gpx_file):
        self._data = etree.parse(gpx_file)
        self._xmlns = self._data.getroot().nsmap[None]
        nsmap = self._data.getroot().nsmap
        self._trkpt_path = '{%s}trk/{%s}trkseg/{%s}trkpt' % (self._xmlns, self._xmlns, self._xmlns)

    def replace_elevation(self, trackpoints, error_tolerance = 10, min_elevation = 0, max_elevation = 5000):
        # We assume that elevation correction fails when more than 10% of points fail
        # TODO: move optional parameters to extension configuration so user can set his/her preferences
        ele_fixed = True
        ele_fixed_fail = 0
        num_trackpoints = len(trackpoints)
        logging.info("Correcting elevation for %d trackpoints" %num_trackpoints)
        logging.info("Error tolerance: %d%%, min elevation: %dm, max elevation: %dm" %(error_tolerance, min_elevation, max_elevation))
        for trkpt in trackpoints:
            lat = float(trkpt.attrib['lat'])
            lon = float(trkpt.attrib['lon'])
            ele = trkpt.find('{%s}ele' % self._xmlns)
            ele_new = self._srtm.get_elevation(lat, lon)
            if ele_new:
                if min_elevation < ele_new < max_elevation:
                    logging.debug("Setting point (lat=%s, lon=%s) elevation to %s" %(lat, lon, ele_new))
                    ele.text = str(ele_new)
                else:
                    logging.info("Discarding strange elevation (%dm) found for point (lat=%s, lon=%s)" %(ele_new, lat, lon))
                    ele_fixed_fail += 1
            else:
                ele_fixed_fail += 1
                logging.debug("Not able to find elevation for point (lat=%s, lon=%s)" %(lat, lon))
            # Division in python 2.x truncates, in 3.x returns float
            if ele_fixed_fail > num_trackpoints/error_tolerance:
                logging.info("Error tolerance exceeded (%d points failed), aborting elevation correction" %ele_fixed_fail)
                ele_fixed = False
                break
        return ele_fixed

def backup_file(orig_file):
    backup = orig_file + "_orig"
    if not os.path.isfile(backup):
        logging.debug("Copying original file %s to %s" %(orig_file, backup))
        try:
            shutil.copy(orig_file, backup)
        except:
            logging.error('Not able to copy %s' %orig_file)
            traceback.print_exc()
    else:
        # Should we exit?
        logging.info("Backup file %s already exists. Trying to correct altitude more than once?" %backup)

def encode_coord(x, prev):
    val = int(x * 1e5)
    return encode_signed(val - prev), val

def encode_signed(n):
    tmp = n << 1
    if n < 0:
        tmp = ~tmp
    return encode_unsigned(tmp)

def encode_unsigned(n):
    b = []
    while n >= 32:
        b.append(n & 31)
        n = n >> 5
    b = [(c | 0x20) for c in b]
    b.append(n)
    b = [(i + 63) for i in b]
    return ''.join([chr(i) for i in b])

