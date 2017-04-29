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

import os
import sys
import shutil
import logging

import gtk
import httplib2

import wordpresslib     #TODO remove need for this library
from pytrainer.extensions.googlemaps import Googlemaps
import pytrainer.lib.points as Points
from pytrainer.lib.date import Date
from pytrainer.lib.uc import UC

class wordpress:
    def __init__(self, parent = None, pytrainer_main = None, conf_dir = None, options = None):
        #TODO could use some logging
        self.parent = parent
        self.pytrainer_main = pytrainer_main
        self.uc = UC()
        self.options = options
        self.conf_dir = conf_dir
        self.tmpdir = self.pytrainer_main.profile.tmpdir
        self.data_path = self.pytrainer_main.profile.data_path
        self.googlemaps = Googlemaps(data_path=self.data_path, pytrainer_main=pytrainer_main)
        self.wp = None

    def run(self, id, activity=None):
        #Show user something is happening
        msg = _("Posting to Wordpress blog")
        md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_NONE, msg)
        md.set_title(_("Wordpress Extension Processing"))
        md.set_modal(True)
        md.show()
        while gtk.events_pending(): # This allows the GUI to update
            gtk.main_iteration()    # before completion of this entire action
        logging.debug("before request posting")
        options = self.options
        self.wordpressurl = options["wordpressurl"]
        self.user = options["wordpressuser"]
        self.password = options["wordpresspass"]
        self.gpxfile = "%s/gpx/%s.gpx" %(self.conf_dir,id)
        self.googlekey = options["googlekey"]
        self.idrecord = id
        self.activity = activity
        self.wordpresscategory = options["wordpresscategory"]
        debug_msg = "%s, %s, %s, %s, %s, %s" % (self.wordpressurl, self.user, self.gpxfile, self.googlekey, self.idrecord, self.wordpresscategory)
        logging.debug(debug_msg)
        try:
            self.wp = wordpresslib.WordPressClient(self.wordpressurl, self.user, self.password) #TODO remove need for wordpresslib??
            self.error = False
        except Exception as e:
            print e
            self.error = True
            self.log = "Url, user or pass are incorrect. Please, check your configuration"
        self.loadRecordInfo()
        if self.title is None or self.title == "":
            self.title = "Untitled Activity"
        blog_table = self.createTable()
        blog_route = self.createRoute()
        blog_body = self.createBody()

        blog_figureHR = self.createFigureHR()
        blog_figureStage = self.createFigureStage()
        blog_foot = self.createFoot()

        self.description = "<![CDATA["+blog_body+blog_table+blog_route+blog_figureHR+blog_figureStage+blog_foot+"]]>"
        xmlstuff = '''<methodCall>
<methodName>metaWeblog.newPost</methodName>
<params>
<param>
<value>
<string>MyBlog</string>
</value>
</param>
<param>
<value>%s</value>
</param>
<param>
<value>
<string>%s</string>
</value>
</param>
<param>
<struct>
<member>
<name>categories</name>
<value>
<array>
<data>
<value>%s</value>
</data>
</array>
</value>
</member>
<member>
<name>description</name>
<value>%s</value>
</member>
<member>
<name>title</name>
<value>%s</value>
</member>
</struct>
</param>
<param>
 <value>
  <boolean>1</boolean>
 </value>
</param>
</params>
</methodCall>
''' % (self.user, self.password, self.wordpresscategory,  self.description, self.title)

        #POST request to Wordpress blog
        h = httplib2.Http()
        res, content = h.request(self.wordpressurl, 'POST', body=xmlstuff)
        logging.debug("after request posting")
        logging.debug("Got response status: %s, reason: %s, content: %s" % (res.status, res.reason, content))
        if res.reason == 'OK':
            res_msg = "Successfully posted to Wordpress."
        else:
            res_msg = "Some error occured\nGot a status %s, reason %s\nContent was: %s" % (res.status, res.reason, content)
        #Close 'Please wait' dialog
        md.destroy()
        #Show the user the result
        md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, res_msg)
        md.set_title(_("Wordpress Extension Upload Complete"))
        md.set_modal(False)
        md.run()
        md.destroy()

    def createRoute(self):
        gpxpath = "%s/gpstrace.gpx.txt" % self.tmpdir
        #htmlpath = "%s/index.html" % self.tmpdir
        kmlpath = "%s/gps.kml.txt" % self.tmpdir
        description_route = ''
        if os.path.isfile(self.gpxfile):
            #copy gpx file to new name
            shutil.copy(self.gpxfile, gpxpath)
            #create the html file
            #htmlpath = googlemaps.drawMap(self.gpxfile,self.googlekey,htmlpath)    #TODO fix to use main googlemaps and remove extensions copy
            htmlpath = self.googlemaps.drawMap(self.activity)
            #create the kml file
            os.system("gpsbabel -t -i gpx -f %s -o kml,points=0,line_color=ff0000ff -F %s" %(self.gpxfile,kmlpath)) #TODO fix to remove gpsbabel

            #gfile = self.wp.newMediaObject(self.gpxfile)
            gfile = self.wp.newMediaObject(gpxpath)
            hfile = self.wp.newMediaObject(htmlpath)
            kfile = self.wp.newMediaObject(kmlpath)

            description_route = '''<strong>Map: </strong> <br/>
            <iframe width='480' height='480' src='%s'> Need frame support </iframe><br/>
            <a href='%s'>Gpx-format</a> <a href='%s'>Kml-format (GoogleEarth)</a><br/><br/>''' %(hfile,gfile,kfile)
        return description_route

    def loadRecordInfo(self):
        #date = Date()
        #record = self.pytrainer_main.record.getrecordInfo(self.idrecord)[0]
        #"sports.name,date,distance,time,beats,comments,average,calories,id_record,title,upositive,unegative,maxspeed,maxpace,pace,maxbeats,date_time_utc,date_time_local",
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

    def createBody(self):
        if self.comments is None or self.comments == "":
            return ""
        else:
            return '''<b> Description: </b><br/>%s<br/>''' %self.comments

    def createTable(self):
        description_table = '''
            <br/>
            <table border=0>
                <tr>
                    <td><strong>Activity:</strong></td>
                    <td>%s</td>
                    <td><strong>Date:</strong></td>
                    <td>%s</td>
                </tr>
                <tr>
                    <td><strong>Distance (%s):</strong></td>
                    <td>%.2f</td>
                    <td><strong>Time (hh:mm:ss):</strong></td>
                    <td>%s</td>
                </tr>
                <tr>
                    <td><strong>Max speed (%s):</strong></td>
                    <td>%.2f</td>
                    <td><strong>Avg speed (%s):</strong></td>
                    <td>%.2f</td>
                </tr>
                <tr>
                    <td><strong>Max pace (%s):</strong></td>
                    <td>%.2f</td>
                    <td><strong>Avg pace (%s):</strong></td>
                    <td>%.2f</td>
                </tr>
                <tr>
                    <td><strong>Max pulse:</strong></td>
                    <td>%s</td>
                    <td><strong>Avg pulse:</strong></td>
                    <td>%s</td>
                </tr>
                <tr>
                    <td><strong>Acc elevation (+%s):</strong></td>
                    <td>%.2f</td>
                    <td><strong>Acc elevation (-%s):</strong></td>
                    <td>%.2f</td>
                </tr>
            </table>
            ''' %(  self.sport, self.date, self.uc.unit_distance, self.distance, self.time, self.uc.unit_speed, self.maxspeed,
                    self.uc.unit_speed, self.average, self.uc.unit_pace, self.maxpace, self.uc.unit_pace, self.pace,
                    self.maxbeats, self.beats, self.uc.unit_height, self.upositive, self.uc.unit_height, self.unegative)
        return description_table

    def createFigureHR(self):
        hr_fig_path = "%s/hr.png" % self.tmpdir #TODO ensure png exists
        blog_figures = ''
        # If there are no graphs, return empty string.
        if os.path.isfile(hr_fig_path):
            #the graph files are created because the graph tabs are automatically visited (which invokes graph generation)
            hrfile = self.wp.newMediaObject(hr_fig_path)
            blog_figures = '''<br/> <img src='%s' /> ''' %hrfile
        return blog_figures

    def createFigureStage(self):
        stage_fig_path = "/tmp/stage.png"   #TODO fix, correct tmp dir and ensure png exists
        blog_figures = ''
        # If there are no graphs, return empty string.
        if os.path.isfile(stage_fig_path):
            #the graph files are created because the graph tabs are automatically visited (which invokes graph generation)
            stagefile = self.wp.newMediaObject(stage_fig_path)
            blog_figures = '''<br/> <img src='%s' /> ''' %stagefile
        return blog_figures

    def createFoot(self):
        return ''' <br/><center>Powered by <a href='https://github.com/pytrainer/pytrainer'>pytrainer</a></center>'''

    def createTitle(self):
        if self.title==None:
            self.error = True
            self.log = "A Title must be defined. Please, configure the record properly"
        return self.title

    def createCategory(self):
        if self.wordpresscategory==None:
            self.error = True
            self.log = "A wordpress category must be defined. Please, configure the wordpress extension"
        else:
            return ([self.wordpresscategory])
