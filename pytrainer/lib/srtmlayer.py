#!/usr/bin/env python
import os, stat, sys
import logging

import random, re, urllib2, zipfile
from math import floor, ceil
from cStringIO import StringIO
from osgeo import gdal, gdalnumeric

from pytrainer.lib.srtmtiff import SrtmTiff

"""
A list of servers providing SRTM data in GeoTIFF 
"""
srtm_server_list = [
               {'url' : 'http://droppr.org/srtm/v4.1/6_5x5_TIFs/', 'ext' : '.zip', 'active' : True },  \
               {'url' : 'ftp://xftp.jrc.it/pub/srtmV4/tiff/'     , 'ext' : '.zip', 'active' : True }, \
               {'url' : 'http://srtm.csi.cgiar.org/SRT-ZIP/SRTM_V41/SRTM_Data_GeoTiff/' , 'ext' : '.zip' , 'active' : True }, \
               {'url' : 'ftp://srtm.csi.cgiar.org/SRTM_V41/SRTM_Data_GeoTiff/' , 'ext' : '.zip' , 'active' : True }, \
               {'url' : 'http://hypersphere.telascience.org/elevation/cgiar_srtm_v4/tiff/zip/', 'ext' : '.ZIP', 'active' : False }
              ]
srtm_server = srtm_server_list[0]


class SrtmLayer(object):
    """
    Provides an interface to SRTM elevation data stored in GeoTIFF files.
    Files are automaticly downloaded from mirror server and cached.
    
    Sample usage:
    
        >>> lat = 52.25
        >>> lon = 16.75
        >>> srtm = SrtmLayer()
        >>> ele = srtm.get_elevation(lat, lon)
        >>> round(ele, 4)
        63.9979
        
    """
    _cache = {}
    
    def _download_srtm_tiff(self, srtm_filename):
        """
        Download and unzip GeoTIFF file.
        """
        #msg = _("Downloading SRTM Data from server. This might take some time...")
        #md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_NONE, msg)
        #md.set_title(_("Downloading SRTM Data"))
        #md.set_modal(True)
        #md.show()
        
        srtm_dir = os.path.expanduser('~/.pytrainer/SRTM_data')
        if not os.path.isdir(srtm_dir):
            os.mkdir(srtm_dir)        
        
        logging.info('Downloading SRTM data file, it may take some time ...')        
        #url = 'http://hypersphere.telascience.org/elevation/cgiar_srtm_v4/tiff/zip/%s.ZIP' % srtm_filename[:-4]
        url = '%s%s%s' % (srtm_server['url'], srtm_filename[:-4],srtm_server['ext'] ) 
        print "Attempting to get URL: %s" % url
        zobj = StringIO()
        zobj.write(urllib2.urlopen(url).read())
        z = zipfile.ZipFile(zobj)
        print "Got URL: %s" % url
        
        srtm_path = os.path.join(srtm_dir, srtm_filename)
        out_file = open(srtm_path, 'w')
        out_file.write(z.read(srtm_filename))
        
        z.close()
        out_file.close()
        #md.destroy()

        
    def get_srtm_filename(self, lat, lon):
        """
        Filename of GeoTIFF file containing data with given coordinates.
        """
        colmin = floor((6000 * (180 + lon)) / 5)
        rowmin = floor((6000 * (60 - lat)) / 5)
    
        ilon = ceil(colmin / 6000.0)
        ilat = ceil(rowmin / 6000.0)
        
        #return 'srtm_%02d_%02d.TIF' % (ilon, ilat)
        return 'srtm_%02d_%02d.tif' % (ilon, ilat)
        
    def get_elevation(self, lat, lon):
        """
        Returns the elevation in metres of point (lat, lon).
        """
        srtm_filename = self.get_srtm_filename(lat, lon)
        if srtm_filename not in self._cache:
            srtm_path = os.path.join(os.path.expanduser('~/.pytrainer/SRTM_data'), srtm_filename)
            if not os.path.isfile(srtm_path):
                self._download_srtm_tiff(srtm_filename)
            else:
                print "File already downloaded (%s)" % srtm_filename
                            
            self._cache[srtm_filename] = SrtmTiff(srtm_path)
        
        srtm = self._cache[srtm_filename]
        return srtm.get_elevation(lat, lon)
