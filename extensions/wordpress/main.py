#!/usr/bin/env python
import wordpresslib
import points as Points
from optparse import OptionParser
import os
import googlemaps
from pytrainer.lib.ddbb import DDBB
from pytrainer.lib.xmlUtils import XMLParser

class Main:
	def __init__(self,options):
		self.wordpressurl = options.wordpressurl
		self.user = options.wordpressuser
		self.password = options.wordpresspass
		self.gpxfile = options.gpxfile
		self.googlekey = options.googlekey
		self.conffile = options.conffile
		self.idrecord = options.idrecord
		self.wordpresscategory = options.wordpresscategory
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

			description_route = '''<strong>Route: <strong> <br/>
			<iframe width='520' height='480' src='%s'> Need frame support </iframe><br/>
			<a href='%s'>Gpx file</a> <a href='%s'>Kml file (GoogleEarth)</a><br/><br/>''' %(hfile,gfile,kfile)
		return description_route

	def loadRecordInfo(self):
		configuration = XMLParser(self.conffile)
		ddbb = DDBB(configuration)
		ddbb.connect()
		recordinfo = ddbb.select("records,sports",
			"sports.name,date,distance,time,beats,comments,average,calories,id_record,title,upositive,unegative",
			"id_record=\"%s\" and records.sport=sports.id_sports" %self.idrecord)
		recordinfo = recordinfo[0]
		self.title = recordinfo[9]
		self.sport = recordinfo[0]
		self.date = recordinfo[1]
		self.distance = recordinfo[2]
		self.time = recordinfo[3]
		self.beats = recordinfo[4]
		self.comments = recordinfo[5]
		self.average = recordinfo[6]
		self.calories = recordinfo[7]
		self.upositive = recordinfo[10]
		self.unegative = recordinfo[11]

	def createBody(self):
		return '''<b> Descripcion: <b/><br/>
%s<br/>''' %self.comments
	
	def createTable(self):
		description_table = '''
			<br/>
			<table border=0>
				<tr>
					<td><strong>Deporte:</strong></td>
					<td>%s</td>
					<td><strong>Fecha:</strong></td>
					<td>%s</td>
				</tr>
				<tr>
					<td><strong>Distancia:</strong></td>
					<td>%s</td>
					<td><strong>Tiempo:</strong></td>
					<td>%s</td>
				</tr>
				<tr>
					<td><strong>Calorias:</strong></td>
					<td>%s</td>
					<td><strong>Media:</strong></td>
					<td>%s</td>
				</tr>
				<tr>
					<td><strong>Desnivel Positivo:</strong></td>
					<td>%s</td>
					<td><strong>Desnivel Negativo:</strong></td>
					<td>%s</td>
				</tr>
			</table>					
			''' %(self.sport,self.date,self.distance,self.time,self.calories,self.average,self.upositive,self.unegative)
		return description_table

	def createFoot(self):
		return ''' <center>Powered by <a href='http://pytrainer.e-oss.net'>Pytrainer</a></center>'''
	
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
			blog_foot = self.createFoot()
			
			self.wp.selectBlog(0)
	
			post = wordpresslib.WordPressPost()
			post.title = blog_title
			post.description = blog_body+blog_table+blog_route+blog_foot
			post.categories = blog_category
			idNewPost = self.wp.newPost(post, False)
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
parser.add_option("-f", "--conffile", dest="conffile")
(options,args) =  parser.parse_args()

main = Main(options)
print main.run()
