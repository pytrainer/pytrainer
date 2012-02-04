# -*- coding: iso-8859-1 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net

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
from subprocess import call

class RunScriptExtension:
    def __init__(self, parent = None, pytrainer_main = None, conf_dir = None, options = None):
        self.parent = parent
        self.pytrainer_main = pytrainer_main
        self.options = options
        self.conf_dir = conf_dir
        self.tmpdir = self.pytrainer_main.profile.tmpdir
        self.data_path = self.pytrainer_main.profile.data_path
        self.wp = None

    def run(self, id, activity=None):
        #Show user something is happening
        msg = _("Running Script ...")
        md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_NONE, msg)
        md.set_title(_("Passing data to Script"))
        md.set_modal(True)
        md.show()
        while gtk.events_pending(): # This allows the GUI to update
            gtk.main_iteration()    # before completion of this entire action
        options = self.options
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
        ret = call(args)
        md.destroy()
        if ret == 0:
            res_msg="OK"
        else:
            res_msg="Error"      
        md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, res_msg)
        md.set_title(_("Script has Run"))
        md.set_modal(False)
        md.run()
        md.destroy()

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

    
