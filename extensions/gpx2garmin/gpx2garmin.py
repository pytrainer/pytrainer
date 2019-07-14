from gi.repository import Gtk
import subprocess
import re

class gpx2garmin:
    def __init__(self, parent = None, pytrainer_main = None, conf_dir = None, options = None):
        self.limit = options["gpx2garminmaxpoints"]
        self.device = options["gpx2garmindevice"]
        self.conf_dir = conf_dir
        self.gpxfile = None
        self.tmpgpxfile = "/tmp/_gpx2garmin.gpx"
        self.pytrainer_main = pytrainer_main

    def prepareGPX(self):
        ' create an output file and insert a name into the <trk> stanza '
        f = open(self.tmpgpxfile, 'w')
        name = 'default'
        for line in open(self.gpxfile):
            if re.search('^<name>.+</name>$', line):
                name = line
            elif re.search('^<trk>$', line):
                line = '%s%s' % (line, name)
            f.write(line)
        f.close()
        
    def exportGPX(self):
        ' export the GPX file using gpsbabel '
        cmd = ["gpsbabel", "-t", "-i", "gpx", "-f", self.tmpgpxfile, "-o", "garmin"]
        if self.limit is not None:
            cmd = cmd + ["-x", "simplify,count=%s" % self.limit]
        cmd = cmd + ["-F", self.device]
        return subprocess.call(cmd)

    def run(self, id, activity=None):
        ' main extension method '
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
        md = Gtk.MessageDialog(self.pytrainer_main.windowmain.window1, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, self.log)
        md.set_title(_("gpx2garmin Extension"))
        md.set_modal(False)
        md.run()
        md.destroy()
