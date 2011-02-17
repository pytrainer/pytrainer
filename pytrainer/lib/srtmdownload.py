# -*- coding: iso-8859-1 -*-

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

import os
import gtk
import urllib2
import zipfile
from cStringIO import StringIO
import logging

"""
A list of servers providing SRTM data in GeoTIFF.
"""
srtm_server_list = [
    {'url' : 'http://hypersphere.telascience.org/elevation/cgiar_srtm_v4/tiff/zip/', 'ext' : '.ZIP', 'active' : False }, \
    {'url' : 'http://droppr.org/srtm/v4.1/6_5x5_TIFs/', 'ext' : '.zip', 'active' : True },  \
    {'url' : 'ftp://xftp.jrc.it/pub/srtmV4/tiff/'     , 'ext' : '.zip', 'active' : True }, \
    {'url' : 'http://srtm.csi.cgiar.org/SRT-ZIP/SRTM_V41/SRTM_Data_GeoTiff/' , 'ext' : '.zip' , 'active' : True }, \
    {'url' : 'ftp://srtm.csi.cgiar.org/SRTM_V41/SRTM_Data_GeoTiff/' , 'ext' : '.zip' , 'active' : True }, \
    {'url' : 'http://hypersphere.telascience.org/elevation/cgiar_srtm_v4/tiff/zip/', 'ext' : '.ZIP', 'active' : False }
    ]

global loopActive

class DownloadLoop:
    """ 
    Download GeoTIFF in partial chunks. Between chunks check gtk.min_iteration
    and update progressbar. Threadless Implementation.
    """
    srtm_dir = os.path.expanduser('~/.pytrainer/SRTM_data')
    
    def __init__(self, progressbar, label, tile_name):
        self.progressbar = progressbar
        self.label = label
        self.tile_name = tile_name
        print tile_name
    
    def run(self):
        logging.debug(">>")
        global loopActive
        
        #print 'Loop started', loopActive
                
        srtm_filename = '%s.tif' % self.tile_name
        if not os.path.isdir(self.srtm_dir):
            os.mkdir(self.srtm_dir)             
        
        urlfile = self.get_urlfile()
        if not urlfile:
            return False
        
        try:
            size_total = int(urlfile.info().getheader('Content-Length').strip())
        except:
            size_total = 0

        if size_total == 0:
            loopActive = False
        #print 'Total size:', size_total
        
        size_chunk = 4096 #8192
        size_got = 0
        zobj = StringIO()  
        
        while loopActive:
            while gtk.events_pending():
                gtk.main_iteration(block = False)            
            chunk = urlfile.read(size_chunk)
            size_got+= size_chunk
            if chunk:
                zobj.write( chunk )
                size_rel = min (1.0, size_got / (1.0 * size_total))
                #print "Read %s Percent." % (round(100*size_rel, 1))
                self.progressbar.set_fraction( size_rel )                
            else:
                loopActive = False                
        if size_rel == 1.0:
            print "start unzip"
            z = zipfile.ZipFile(zobj)
            srtm_path = os.path.join(self.srtm_dir, srtm_filename)
            out_file = open(srtm_path, 'w')
            out_file.write(z.read(srtm_filename))
            z.close()
            zobj.close
            out_file.close()
            logging.debug("<<")
            return True     # Hooray, got file                    
        logging.debug("<<")
        return False
            
    def get_urlfile(self):
        """  Go through SRTM Servers """
        logging.debug('--')
        for server in srtm_server_list:
            url = '%s%s%s' % (server['url'], self.tile_name, server['ext']) 
            print "Attempting to get URL: %s" % url
            logging.debug("Attempting to get URL: %s" % url)
            try:
                urlfile = urllib2.urlopen( url )
                self.label.set_text(str(url))
                return urlfile
            except:
                print '%s FAILED' % url
                logging.debug('%s FAILED' % url)
                pass


def main_quit(obj):
    logging.debug("--")
    global loopActive
    print 'main_quit entered'
    loopActive = False

def download(tile_name):
    logging.debug(">>")
    global loopActive
    loopActive = True
    result = False
    window = gtk.Dialog()
    window.set_title('Download GeoTIFF')
    labelH = gtk.Label('<b>Downloading Tile %s</b>' % tile_name)
    labelH.set_use_markup(True)
    labelH.set_alignment(0, 1)
    
    label = gtk.Label('Searching for Server ...')
    progressbar = gtk.ProgressBar()

    window.connect('destroy', main_quit)
    button = gtk.Button(stock=gtk.STOCK_CANCEL)
    button.connect("clicked", main_quit)

    window.vbox.pack_start(labelH, expand=False, padding=3)
    window.vbox.pack_start(label, expand=False, padding=3)
    window.vbox.pack_start(progressbar, expand=False, padding=3)
    window.action_area.pack_start(button, expand=False)
    window.show_all()

    lp = DownloadLoop(progressbar, label, tile_name)
    result = lp.run()
    try:
        window.destroy()
    except:
        pass
    logging.debug("<<")
    return result
