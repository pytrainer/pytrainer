#!/usr/bin/env python
import os #, stat, sys
import logging
import gtk
#import random, re, urllib2, zipfile
#from math import floor, ceil
#from cStringIO import StringIO
#from optparse import OptionParser
#from osgeo import gdal, gdalnumeric
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

    def run(self, id, activity=None):  #TODO Convert to use activity...
        logging.debug(">>")
        gpx_file = "%s/gpx/%s.gpx" % (self.conf_dir, id)
        if os.path.isfile(gpx_file):
            # Backup original raw data as *.orig.gpx
            orig_file = open(gpx_file, 'r')
            orig_data = orig_file.read()
            orig_file.close()
            backup_file = open("%s/gpx/%s.orig.gpx" % (self.conf_dir, id), 'w')
            backup_file.write(orig_data)
            backup_file.close()
            #GPX file is ok and found, so open it
            logging.debug("ELE GPX file: %s found, size: %d" % (gpx_file, os.path.getsize(gpx_file)))

            
            
            """
            Parse GPX file to ElementTree instance.
            """
            self._data = etree.parse(gpx_file)
            self._xmlns = self._data.getroot().nsmap[None]
            self._trkpt_path = '{%s}trk/{%s}trkseg/{%s}trkpt' % (self._xmlns, self._xmlns, self._xmlns)

            """
            Replace elevation from GPX by data from SRTM.
            TODO (Arnd) make a function within class fixelevation out of this for better reuse
            """
            for trkpt in self._data.findall(self._trkpt_path):
                lat = float(trkpt.attrib['lat'])
                lon = float(trkpt.attrib['lon'])
            
                ele = trkpt.find('{%s}ele' % self._xmlns)
                if ele is not None:
                    ele.text = str(self._srtm.get_elevation(lat, lon))
                else:
                    ele = etree.Element('ele')
                    ele.text = str(self._srtm.get_elevation(lat, lon))
                    trkpt.append(ele)
            """
            write out to original *.gpx. 
            """
            self._data.write( gpx_file, 
                                encoding=self._data.docinfo.encoding, 
                                xml_declaration=True, 
                                pretty_print=False)


            #print trkpt
            res_msg = "Elevation has been fixed."
            #Show the user the result
            md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, res_msg)
            md.set_title(_("Elevation Correction Complete"))
            md.set_modal(False)
            md.run()
            md.destroy()
            #TODO reload gpx data in main window 
            
        else:
            logging.error("ELE GPX file: %s NOT found!!!" % (gpx_file))
        logging.debug("<<")




