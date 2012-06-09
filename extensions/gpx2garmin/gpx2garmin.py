#!/usr/bin/env python

import gtk
import subprocess
import os

class gpx2garmin:
    def __init__(self, parent = None, pytrainer_main = None, conf_dir = None, options = None):
        self.limit = options["gpx2garminmaxpoints"]
        self.device = options["gpx2garmindevice"]
        self.conf_dir = conf_dir
        self.gpxfile = None
        self.tmpgpxfile = "/tmp/_gpx2garmin.gpx"
        self.pytrainer_main = pytrainer_main

    def prepareGPX(self):
        # add a name to the gpx data in the <trk> stanza
        os.system('grep "<name>.*</name>" %s > /tmp/_gpx2garmin' % self.gpxfile)
        os.system('sed "/<trk>/r /tmp/_gpx2garmin" %s > %s' % (self.gpxfile, self.tmpgpxfile))
        
    def exportGPX(self):
        cmd = ["gpsbabel", "-t", "-i", "gpx", "-f", self.tmpgpxfile, "-o", "garmin"]
        if self.limit is not None:
            cmd = cmd + ["-x", "simplify,count=%s" % self.limit]
        cmd = cmd + ["-F", self.device]
        return subprocess.call(cmd)

    def run(self, id, activity=None):
        self.gpxfile = "%s/gpx/%s.gpx" % (self.conf_dir, id)
        self.log = "Export "
        try:
            self.prepareGPX()
            if self.exportGPX() == 1:
                # assume no device present?
                self.log = self.log + "failed - no device present?"
            else:
                self.log = self.log + "succeeded!" 
        except:
            self.log = self.log + "failed!"
        md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, self.log)
        md.set_title(_("gpx2garmin Extension"))
        md.set_modal(False)
        md.run()
        md.destroy()
