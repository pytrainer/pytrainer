#!/usr/bin/env python
import os, stat, sys
import logging

import random, re, urllib2, zipfile
from math import floor, ceil
from osgeo import gdal, gdalnumeric

from pytrainer.lib.srtmtiff import SrtmTiff
import srtmdownload

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
      
    def get_srtm_filename(self, lat, lon):
        """
        Filename of GeoTIFF file containing data with given coordinates.
        """
        colmin = floor((6000 * (180 + lon)) / 5)
        rowmin = floor((6000 * (60 - lat)) / 5)
    
        ilon = ceil(colmin / 6000.0)
        ilat = ceil(rowmin / 6000.0)
        
        return 'srtm_%02d_%02d.tif' % (ilon, ilat)
        
    def get_elevation(self, lat, lon):
        """
        Returns the elevation in metres of point (lat, lon).
        """
        srtm_filename = self.get_srtm_filename(lat, lon)
        if srtm_filename not in self._cache:
            srtm_path = os.path.join(os.path.expanduser('~/.pytrainer/SRTM_data'), srtm_filename)
            if not os.path.isfile(srtm_path):
                result = srtmdownload.download( srtm_filename[:-4] )
                if not result:
                    return False
            else:
                logging.info("File already downloaded (%s)", srtm_filename)
                            
            self._cache[srtm_filename] = SrtmTiff(srtm_path)
        
        srtm = self._cache[srtm_filename]
        return srtm.get_elevation(lat, lon)
