#!/usr/bin/env python
import os
from scipy.ndimage import gaussian_filter1d
import numpy as np
import logging
import gtk
import re
from lxml import etree


class smoothelevation:
    _data = None

    def __init__(self, parent=None, pytrainer_main=None, conf_dir=None,
                 options=None):
        self.parent = parent
        self.pytrainer_main = pytrainer_main
        self.options = options
        self.conf_dir = conf_dir

    def run(self, aid, activity=None):
        logging.debug(">>")
        logging.debug("Begining GPX elevation smoothing.")
        gpx_file = "%s/gpx/%s.gpx" % (self.conf_dir, aid)
        if os.path.isfile(gpx_file):
            orig_file = open(gpx_file, 'r')
            orig_data = orig_file.read()
            orig_file.close()
            # Back up original gpx data
            if not(os.path.isfile("%s/gpx/%s.orig.gpx" % (self.conf_dir, aid))):
                backup_file = open("%s/gpx/%s.orig.gpx" %
                                   (self.conf_dir, aid), 'w')
                backup_file.write(orig_data)
                backup_file.close()
                logging.debug("ELE GPX file: %s backed up as %s/gpx/%s.orig.gpx" %
                              (aid, self.conf_dir, aid))
            logging.debug("ELE GPX file: %s found, size: %d" %
                          (gpx_file, os.path.getsize(gpx_file)))

            """
            Parse GPX file to ElementTree instance.
            """
            self._data = etree.parse(gpx_file)
            self._xmlns = self._data.getroot().nsmap[None]
            self._trkpt_path = '{%s}trk/{%s}trkseg/{%s}trkpt' % \
                               (self._xmlns, self._xmlns, self._xmlns)

            """
            Load elevation data, smooth in place, and replace.
            (TODO) Add user-selectable smoothing windows and width
            """
            sigma = 4
            trackpoints = self._data.findall(self._trkpt_path)
            elev = []
            for trkpt in trackpoints:
                for entry in trkpt.getchildren():
                    if re.search('ele', entry.tag):
                        elev.append(float(entry.text))

            smo_elev = gaussian_filter1d(np.array(zip(range(len(elev)), elev)).T,
                                         sigma)

            logging.debug("Replacing old elevation values")
            for elepair in zip(trackpoints, smo_elev[1, :]):
                for entry in trkpt.getchildren():
                    if re.search('ele', entry.tag):
                        entry.text = str(elepair[1])

            logging.debug("Overwriting old GPX file: %s" % (gpx_file))
            self_data.write(gpx_file,
                            encoding=self._data.docinfo.encoding,
                            pretty_print=False)
            logging.debug("Successfully updated GPX file")
            res_msg = "Elevation has been smoothed by %i" % (sigma)
            self.pytrainer_main.activitypool.remove_activity(aid)
            md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, res_msg)
            md.set_title(_("Elevation smoothing complete"))
            md.set_modal(False)
            md.run()
            md.destroy()

        else:
            logging.error("ELE GPX file: %s NOT found!!!" % (gpx_file))
        logging.debug("<<")
