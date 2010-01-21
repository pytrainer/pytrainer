#!/usr/bin/env python
from optparse import OptionParser
import os
import sys
import SOAPpy

import wordpresslib
import googlemaps
import pytrainer.lib.points as Points
from pytrainer.lib.date import Date

class Main:
	def __init__(self,options):
		self.wordpressurl = options.wordpressurl
		self.user = options.wordpressuser
		self.password = options.wordpresspass
		self.gpxfile = options.gpxfile
		self.googlekey = options.googlekey
		self.idrecord = options.idrecord
		self.wordpresscategory = options.wordpresscategory
      		self.webserviceserver = SOAPpy.SOAPProxy("http://localhost:8081/")
		try: 
			self.wp = wordpresslib.WordPressClient(self.wordpressurl, self.user, self.password)
			self.error = False
		except:
			self.error = True
			self.log = "Url, user or pass are incorrect. Please, check your configuration"
	
	def createRoute(self):
		htmlpath = "/tmp/index.html"
		kmlpath = "/tmp/gps.kml"
		description_route = ''
		if os.path.isfile(self.gpxfile):
			#create the html file
			googlemaps.drawMap(self.gpxfile,self.googlekey,htmlpath)
			#create the kml file
			os.system("gpsbabel -t -i gpx -f %s -o kml,points=0,line_color=ff0000ff -F %s" %(self.gpxfile,kmlpath))
			
			gfile = self.wp.newMediaObject(self.gpxfile)
			hfile = self.wp.newMediaObject(htmlpath)
			kfile = self.wp.newMediaObject(kmlpath)

			description_route = '''<strong>Map: </strong> <br/>
			<iframe width='480' height='480' src='%s'> Need frame support </iframe><br/>
			<a href='%s'>Gpx-format</a> <a href='%s'>Kml-format (GoogleEarth)</a><br/><br/>''' %(hfile,gfile,kfile)
		return description_route

	def loadRecordInfo(self):
		date = Date()
      		record = self.webserviceserver.getRecordInfo(self.idrecord)
		self.sport = record["sport"]
                self.date = record["date"]
                self.distance = record["distance"]
                self.time = date.second2time(float(record["time"]))
                self.beats = record["beats"]
                self.comments = record["comments"]
                self.average = record["average"]
                self.calories = record["calories"]
                self.title = record["title"]
                self.upositive = record["upositive"]
                self.unegative = record["unegative"]
                self.unegative = record["unegative"]
                self.maxspeed = record["maxspeed"]
                self.maxpace = record["maxpace"]
                self.pace = record["pace"]
                self.maxbeats = record["maxbeats"]

	def createBody(self):
		return '''<b> Description: </b><br/>
%s<br/>''' %self.comments
	
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
		hr_fig_path = "/tmp/hr.png"
		blog_figures = ''
		# If there are no graphs, return empty string.
		if os.path.isfile(hr_fig_path):
			#the graph files are created because the graph tabs are automatically visited (which invokes graph generation)
			hrfile = self.wp.newMediaObject(hr_fig_path)
			blog_figures = '''<br/> <img src='%s' /> ''' %hrfile
		return blog_figures

	def createFigureStage(self):
		stage_fig_path = "/tmp/stage.png"
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
			self.log = "A Title must be defined. Please, configure the record propierly"
		return self.title
	
	def createCategory(self):
		if self.wordpresscategory==None:
			self.error = True
			self.log = "A wordpress category must be defined. Please, configure the wordpress extension"
		else:
			return ([self.wordpresscategory])
        					
	def run(self):
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
			return "The post has been submited" 
        				
		else:
			return self.log

parser = OptionParser()
parser.add_option("-d", "--device", dest="device")
parser.add_option("-k", "--googlekey", dest="googlekey")
parser.add_option("-u", "--wordpressuser", dest="wordpressuser")
parser.add_option("-p", "--wordpresspass", dest="wordpresspass")
parser.add_option("-l", "--wordpressurl", dest="wordpressurl")
parser.add_option("-c", "--wordpresscategory", dest="wordpresscategory")
parser.add_option("-g", "--gpxfile", dest="gpxfile")
parser.add_option("-i", "--idrecord", dest="idrecord")
(options,args) =  parser.parse_args()

main = Main(options)
print main.run()
