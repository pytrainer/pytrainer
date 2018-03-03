#!/usr/bin/env python
import os #, stat, sys
import logging
from gi.repository import Gtk
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
        #print activity
        logging.debug(">>")
        gpx_file = "%s/gpx/%s.gpx" % (self.conf_dir, aid)
        ele_fixed = True
        
        if os.path.isfile(gpx_file):
            # Backup original raw data as *.orig.gpx
            #orig_file = open(gpx_file, 'r')
            #orig_data = orig_file.read()
            #orig_file.close()
            #backup_file = open("%s/gpx/%s.orig.gpx" % (self.conf_dir, id), 'w')
            #backup_file.write(orig_data)
            #backup_file.close()
            #GPX file is ok and found, so open it
            logging.debug("ELE GPX file: %s found, size: %d" % (gpx_file, os.path.getsize(gpx_file)))
            
            """
            Parse GPX file to ElementTree instance.
            """
            self._data = etree.parse(gpx_file)
            self._xmlns = self._data.getroot().nsmap[None]
            nsmap = self._data.getroot().nsmap
            pyt_ns = "http://sourceforge.net.project/pytrainer/GPX/0/1"
            PYTRAINER = "{%s}" % pyt_ns
            self._trkpt_path = '{%s}trk/{%s}trkseg/{%s}trkpt' % (self._xmlns, self._xmlns, self._xmlns)

            def addExt(trackpoint, ele_new):
                #Add new elevation to extension tag
                '''
                <extensions>
                    <pytrainer:ele method="srtm_bilinear">31.1</pytrainer:ele>
                </extensions>
                '''
                ext = etree.Element("extensions")
                py_ele = etree.SubElement(ext, PYTRAINER + "ele", method="srtm_bilinear")
                py_ele.text = str(ele_new)
                trackpoint.append(ext)

            """
            Replace elevation from GPX by data from SRTM.
            TODO (Arnd) make a function within class fixelevation out of this for better reuse
            """
            trackpoints = self._data.findall(self._trkpt_path)
            for trkpt in trackpoints:
                lat = float(trkpt.attrib['lat'])
                lon = float(trkpt.attrib['lon'])
            
                ele = trkpt.find('{%s}ele' % self._xmlns)
                ele_new = self._srtm.get_elevation(lat, lon)

                if not ele_new:
                    ele_fixed = False
                    break 

                addExt(trkpt, ele_new)
                
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
                    pass

            if ele_fixed:
                # Write out to original *.gpx.                         
                self._data.write( gpx_file, 
                                encoding=self._data.docinfo.encoding, 
                                xml_declaration=True, 
                                pretty_print=False)
                res_msg = "Elevation has been fixed."
                #TODO Expire activity out of pool - so get updated info
                self.pytrainer_main.activitypool.remove_activity_from_cache(aid)
            else:
                res_msg = "Elevation could not be fixed!"

            #Show the user the result
            md = Gtk.MessageDialog(self.pytrainer_main.windowmain.window1, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, res_msg)
            md.set_title(_("Elevation Correction Complete"))
            md.set_modal(False)
            md.run()
            md.destroy()
            #TODO reload gpx data in main window 
            
        else:
            logging.error("ELE GPX file: %s NOT found!!!" % (gpx_file))
        logging.debug("<<")
        
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

