#!/usr/bin/env python
import os, stat, sys
import logging
import gtk

import random, re, urllib2, zipfile
from math import floor, ceil
from cStringIO import StringIO
from optparse import OptionParser

from osgeo import gdal, gdalnumeric
from lxml import etree

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

# from gpxtools
def bilinear_interpolation(tl, tr, bl, br, a, b):
    """
    Based on equation from:
    http://en.wikipedia.org/wiki/Bilinear_interpolation
    
    :Parameters:
        tl : int
            top-left
        tr : int
            top-right
        bl : int
            buttom-left
        br : int
            bottom-right
        a : float
            x distance to top-left
        b : float
            y distance to top-right

    :Returns: (float)
        interpolated value
    """
    b1 = tl
    b2 = bl - tl
    b3 = tr - tl
    b4 = tl - bl - tr + br

    return b1 + b2 * a + b3 * b + b4 * a * b

class SrtmTiff(object):
    """
    Provides an interface to SRTM elevation data stored in GeoTIFF file.
    
    Based on code from `eleserver` code by grahamjones139.
    http://code.google.com/p/eleserver/
    """
    tile = {}
    
    def __init__(self, filename):
        """
        Reads the GeoTIFF files into memory ready for processing.
        """
        self.tile = self.load_tile(filename)
    
    def load_tile(self, filename):
        """
        Loads a GeoTIFF tile from disk and returns a dictionary containing
        the file data, plus metadata about the tile.

        The dictionary returned by this function contains the following data:
            xsize - the width of the tile in pixels.
            ysize - the height of the tile in pixels.
            lat_origin - the latitude of the top left pixel in the tile.
            lon_origin - the longitude of the top left pixel in the tile.
            lat_pixel - the height of one pixel in degrees latitude.
            lon_pixel - the width of one pixel in degrees longitude.
            N, S, E, W - the bounding box for this tile in degrees.
            data - a two dimensional array containing the tile data.

        """
        dataset = gdal.Open(filename)
        geotransform = dataset.GetGeoTransform()
        xsize = dataset.RasterXSize
        ysize = dataset.RasterYSize
        lon_origin = geotransform[0]
        lat_origin = geotransform[3]
        lon_pixel = geotransform[1]
        lat_pixel = geotransform[5]
        
        retdict = {
            'xsize': xsize,
            'ysize': ysize,
            'lat_origin': lat_origin,
            'lon_origin': lon_origin,
            'lon_pixel': lon_pixel,
            'lat_pixel': lat_pixel,
            'N': lat_origin,
            'S': lat_origin + lat_pixel*ysize,
            'E': lon_origin + lon_pixel*xsize,
            'W': lon_origin,
            'dataset': dataset,
            }
        
        return retdict  

    def pos_from_lat_lon(self, lat, lon):
        """
        Converts coordinates (lat,lon) into the appropriate (row,column)
        position in the GeoTIFF tile data stored in td.
        """
        td = self.tile
        N = td['N']
        S = td['S']
        E = td['E']
        W = td['W']
        lat_pixel = td['lat_pixel']
        lon_pixel = td['lon_pixel']
        xsize = td['xsize']
        ysize = td['ysize']
        
        rowno_f = (lat-N)/lat_pixel
        colno_f = (lon-W)/lon_pixel
        rowno = int(floor(rowno_f))
        colno = int(floor(colno_f))

        # Error checking to correct any rounding errors.
        if (rowno<0):
            rowno = 0
        if (rowno>(xsize-1)):
            rowno = xsize-1
        if (colno<0):
            colno = 0
        if (colno>(ysize-1)):
            colno = xsize-1
            
        return (rowno, colno, rowno_f, colno_f)
    
    def get_elevation(self, lat, lon):
        """
        Returns the elevation in metres of point (lat, lon).
        
        Uses bilinar interpolation to interpolate the SRTM data to the
        required point.
        """
        row, col, row_f, col_f = self.pos_from_lat_lon(lat, lon)

        # NOTE - THIS IS A FIDDLE TO STOP ERRORS AT THE EDGE OF
        # TILES - IT IS NO CORRECT - WE SHOULD GET TWO POINTS 
        # FROM THE NEXT TILE.
        if row==5999: row=5998
        if col==5999: col=5998

        htarr = gdalnumeric.DatasetReadAsArray(self.tile['dataset'], col, row, 2, 2)
        height = bilinear_interpolation(htarr[0][0], htarr[0][1], htarr[1][0], htarr[1][1],
                                       row_f-row, col_f-col)

        return height


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
                            
            self._cache[srtm_filename] = SrtmTiff(srtm_path)
        
        srtm = self._cache[srtm_filename]
        return srtm.get_elevation(lat, lon)

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




