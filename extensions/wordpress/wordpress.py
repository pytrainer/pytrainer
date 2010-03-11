#!/usr/bin/env python
from optparse import OptionParser
import os
import sys

import wordpresslib
import googlemaps
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
		options = self.options
		self.wordpressurl = options["wordpressurl"]
		self.user = options["wordpressuser"]
		self.password = options["wordpresspass"]
		self.gpxfile = "%s/gpx/%s.gpx " %(self.conf_dir,id)
		self.googlekey = options["googlekey"]
		self.idrecord = id #options.idrecord
		self.wordpresscategory = options["wordpresscategory"]
		print self.wordpressurl, self.user, self.password, self.gpxfile, self.googlekey, self.googlekey, self.idrecord, self.wordpresscategory
		
		try: 
			self.wp = wordpresslib.WordPressClient(self.wordpressurl, self.user, self.password)
			self.error = False
		except:
			self.error = True
			self.log = "Url, user or pass are incorrect. Please, check your configuration"
		self.loadRecordInfo()
		blog_title = self.createTitle()
		blog_category = self.createCategory()

		if self.error == False:
			blog_route = self.createRoute()
			blog_body = self.createBody()
			blog_table = self.createTable()
			blog_figureHR = self.createFigureHR()
			blog_figureStage = self.createFigureStage()
			blog_foot = self.createFoot()
			self.wp.selectBlog(0)
	
			post = wordpresslib.WordPressPost()
			post.title = blog_title
			post.description = blog_body+blog_table+blog_route+blog_figureHR+blog_figureStage+blog_foot
			post.categories = blog_category
			idNewPost = self.wp.newPost(post, True)
			print "The post has been submited" #TODO Notification to user
        				
		else:
			print self.log
	
	def createRoute(self):
		htmlpath = "/tmp/index.html" 	#TODO fix to use correct tmp dir
		kmlpath = "/tmp/gps.kml"		#TODO fix to use correct tmp dir
		description_route = ''
		if os.path.isfile(self.gpxfile):
			#create the html file
			googlemaps.drawMap(self.gpxfile,self.googlekey,htmlpath)	#TODO fix to use main googlemaps and remove extensions copy
			#create the kml file
			os.system("gpsbabel -t -i gpx -f %s -o kml,points=0,line_color=ff0000ff -F %s" %(self.gpxfile,kmlpath))	#TODO fix to remove gpsbabel 
			
			gfile = self.wp.newMediaObject(self.gpxfile)
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
