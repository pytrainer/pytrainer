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

import wordpresslib 	#TODO remove need for this library
import googlemaps   	#TODO remove this separate googlemaps class
import pytrainer.lib.points as Points
from pytrainer.lib.date import Date

class wordpress:
	def __init__(self, parent = None, pytrainer_main = None, conf_dir = None, options = None):
		#TODO could use some logging
		self.parent = parent
		self.pytrainer_main = pytrainer_main
		self.options = options
		self.conf_dir = conf_dir

	def run(self, id):
		#Show user something is happening
		msg = _("Posting to Wordpress blog")
		md = gtk.MessageDialog(self.pytrainer_main.windowmain.window1, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_NONE, msg)
		md.set_title(_("Wordpress Extension Processing"))
		md.set_modal(True)
		md.show()
		while gtk.events_pending():	# This allows the GUI to update 
			gtk.main_iteration()	# before completion of this entire action
		logging.debug("before request posting")
		options = self.options
		self.wordpressurl = options["wordpressurl"]
		self.user = options["wordpressuser"]
		self.password = options["wordpresspass"]
		self.gpxfile = "%s/gpx/%s.gpx" %(self.conf_dir,id)
		self.googlekey = options["googlekey"]
		self.idrecord = id #options.idrecord
		self.wordpresscategory = options["wordpresscategory"]
		debug_msg = "%s, %s, %s, %s, %s, %s" % (self.wordpressurl, self.user, self.gpxfile, self.googlekey, self.idrecord, self.wordpresscategory) 
		logging.debug(debug_msg)
		try: 
			self.wp = wordpresslib.WordPressClient(self.wordpressurl, self.user, self.password)	#TODO remove need for wordpresslib??
			self.error = False
		except:
			self.error = True
			self.log = "Url, user or pass are incorrect. Please, check your configuration"
		self.loadRecordInfo()
		if self.title is None:
			self.title = "No Title"
		blog_route = self.createRoute()
		blog_body = self.createBody()
		blog_table = self.createTable()
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
		gpxpath = "/tmp/gpstrace.gpx.txt"
		htmlpath = "/tmp/index.html" 	#TODO fix to use correct tmp dir
		kmlpath = "/tmp/gps.kml.txt"		#TODO fix to use correct tmp dir
		description_route = ''
		if os.path.isfile(self.gpxfile):
			#copy gpx file to new name
			shutil.copy(self.gpxfile, gpxpath)
			#create the html file
			googlemaps.drawMap(self.gpxfile,self.googlekey,htmlpath)	#TODO fix to use main googlemaps and remove extensions copy
			#create the kml file
			os.system("gpsbabel -t -i gpx -f %s -o kml,points=0,line_color=ff0000ff -F %s" %(self.gpxfile,kmlpath))	#TODO fix to remove gpsbabel 
			
			#gfile = self.wp.newMediaObject(self.gpxfile)
			gfile = self.wp.newMediaObject(gpxpath)
			hfile = self.wp.newMediaObject(htmlpath)
			kfile = self.wp.newMediaObject(kmlpath)

			description_route = '''<strong>Map: </strong> <br/>
			<iframe width='480' height='480' src='%s'> Need frame support </iframe><br/>
			<a href='%s'>Gpx-format</a> <a href='%s'>Kml-format (GoogleEarth)</a><br/><br/>''' %(hfile,gfile,kfile)
		return description_route

	def loadRecordInfo(self):
		date = Date()
		record = self.pytrainer_main.record.getrecordInfo(self.idrecord)[0]
		#"sports.name,date,distance,time,beats,comments,average,calories,id_record,title,upositive,unegative,maxspeed,maxpace,pace,maxbeats,date_time_utc,date_time_local",
		self.sport = record[0]
		self.date = record[1]
		self.distance = record[2]
		self.time = date.second2time(float(record[3]))
		self.beats = record[4]
		self.comments = record[5]
		self.average = record[6]
		self.calories = record[7]
		self.title = record[9]
		self.upositive = record[10]
		self.unegative = record[11]
		self.maxspeed = record[12]
		self.maxpace = record[13]
		self.pace = record[14]
		self.maxbeats = record[15]

	def createBody(self):
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
					<td><strong>Distance:</strong></td>
					<td>%s</td>
					<td><strong>Time (hh, mm, ss):</strong></td>
					<td>%s</td>
				</tr>
				<tr>
					<td><strong>Max speed:</strong></td>
					<td>%s</td>
					<td><strong>Avg speed (km/h):</strong></td>
					<td>%s</td>
				</tr>
				<tr>
					<td><strong>Max pace (min/km):</strong></td>
					<td>%s</td>
					<td><strong>Avg pace (min/km):</strong></td>
					<td>%s</td>
				</tr>
				<tr>
					<td><strong>Max pulse:</strong></td>
					<td>%s</td>
					<td><strong>Avg pulse:</strong></td>
					<td>%s</td>
				</tr>
				<tr>
					<td><strong>Acc elevation +:</strong></td>
					<td>%s</td>
					<td><strong>Acc elevation -:</strong></td>
					<td>%s</td>
				</tr>
			</table>					
			''' %(self.sport,self.date,self.distance,self.time,self.maxspeed,self.average,self.maxpace,self.pace,self.maxbeats,self.beats,self.upositive,self.unegative)
		return description_table

	def createFigureHR(self):
		hr_fig_path = "/tmp/hr.png"	#TODO fix, correct tmp dir and ensure png exists
		blog_figures = ''
		# If there are no graphs, return empty string.
		if os.path.isfile(hr_fig_path):
			#the graph files are created because the graph tabs are automatically visited (which invokes graph generation)
			hrfile = self.wp.newMediaObject(hr_fig_path)
			blog_figures = '''<br/> <img src='%s' /> ''' %hrfile
		return blog_figures

	def createFigureStage(self):
		stage_fig_path = "/tmp/stage.png"	#TODO fix, correct tmp dir and ensure png exists
		blog_figures = ''
		# If there are no graphs, return empty string.
		if os.path.isfile(stage_fig_path):
			#the graph files are created because the graph tabs are automatically visited (which invokes graph generation)
			stagefile = self.wp.newMediaObject(stage_fig_path)
			blog_figures = '''<br/> <img src='%s' /> ''' %stagefile
		return blog_figures

	def createFoot(self):
		return ''' <br/><center>Powered by <a href='http://sourceforge.net/projects/pytrainer/'>Pytrainer</a></center>'''
	
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
