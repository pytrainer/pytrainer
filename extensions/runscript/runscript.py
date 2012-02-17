# -*- coding: iso-8859-1 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net
#Copyright (C) Christoph Kluenter <chris@inferno.nadir.org>

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


# used the wordpress extension and changed it to run a script with the data
# of a workout:
# the goal was to tweet from pytrainer.
# I used twidge for the actual tweeting an put this in the  config:
# script: /usr/bin/twidge
# argument: update
# I thought this would be much easier than to write another twitter-client :)
# And it works as advertised :)
# Todo: Make the Arguments to the script configurable

import gtk
import string
import shlex
import subprocess
import threading
import logging

class RunScriptExtension:
    def __init__(self, parent = None, pytrainer_main = None, conf_dir = None, options = None):
        self.parent = parent
        self.pytrainer_main = pytrainer_main
        self.options = options
        self.conf_dir = conf_dir
        self.p = None

    def run(self, id, activity=None):
        options = self.options
        if len(options["script"]) == 0:
            res_msg="You have not configured any script. Please see Help for examples"
            md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, res_msg)
            md.set_title(_("Error"))
            md.set_modal(False)
            md.run()
            md.destroy()
            return
        self.activity = activity
        self.load_record_info()
        inputstring = options["script"]
        inputstring = string.replace(inputstring,"%t",self.title)
        inputstring = string.replace(inputstring,"%s",self.sport)
        inputstring = string.replace(inputstring,"%D",self.date)
        inputstring = string.replace(inputstring,"%T",self.time)
        inputstring = string.replace(inputstring,"%d","%s %s" %(self.distance,self.distance_unit))
        inputstring = string.replace(inputstring,"%p","%.2f %s" %(self.pace,self.pace_unit))
        inputstring = string.replace(inputstring,"%S","%.2f %s" %(self.average,self.speed_unit))
        inputstring = string.replace(inputstring,"%b","%s" % self.beats)
        inputstring = string.replace(inputstring,"%c",self.comments)
        inputstring = string.replace(inputstring,"%C","%s" % self.calories)
        inputstring = string.replace(inputstring,"%mS","%.2f %s" %(self.maxspeed,self.speed_unit))
        inputstring = string.replace(inputstring,"%mp","%.2f %s" %(self.maxpace,self.pace_unit))
        inputstring = string.replace(inputstring,"%mb","%s" %self.maxbeats)

        args = shlex.split(inputstring) 
        res_msg="Script is Running ..."
        self.md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_CANCEL, res_msg)
        self.md.set_title(_(res_msg))
        self.md.set_modal(False)
        self.md.connect('response', self.handle_cancel)
        self.md.show()
        thread = threading.Thread(target=self.run_in_thread, args=(args))
        thread.start()

    def handle_cancel(self, *args):
        if self.p != None:
            self.p.kill()
        self.md.destroy()

    def run_in_thread(self,*popenArgs):
        try:
            self.p = subprocess.Popen(popenArgs)
        except OSError as e:
            logging.debug(e.child_traceback)
        except Exception as e:
            logging.debug(e)
        else:
            self.p.wait()
        self.md.destroy()
        return


    def load_record_info(self):
        self.sport = self.activity.sport_name
        self.date = self.activity.date
        self.distance = self.activity.distance
        self.time = "%d:%02d:%02d" % (self.activity.time_tuple)
        self.beats = self.activity.beats
        self.comments = self.activity.comments
        self.average = self.activity.average
        self.calories = self.activity.calories
        self.title = self.activity.title
        self.upositive = self.activity.upositive
        self.unegative = self.activity.unegative
        self.maxspeed = self.activity.maxspeed
        self.maxpace = self.activity.maxpace
        self.pace = self.activity.pace
        self.maxbeats = self.activity.maxbeats
        self.distance_unit = self.activity.distance_unit
        self.speed_unit = self.activity.speed_unit
        self.pace_unit = self.activity.pace_unit
        self.height_unit = self.activity.height_unit

    
