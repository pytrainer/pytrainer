#!/usr/bin/env python
import wordpresslib
import points as Points
from optparse import OptionParser
import os
import googlemaps
from pytrainer.lib.ddbb import DDBB
from pytrainer.lib.xmlUtils import XMLParser


def main(options):
	wordpress = options.wordpressurl
	user = options.wordpressuser
	password = options.wordpresspass
	gpxfile = options.gpxfile
	googlekey = options.googlekey
	conffile = options.conffile
	idrecord = options.idrecord

	# prepare client object
	try: 
		wp = wordpresslib.WordPressClient(wordpress, user, password)
	except:
		return "Url, user or pass are incorrect. Check your configuration"

	if os.path.isfile(gpxfile):
		gfile = wp.newMediaObject(gpxfile)
		htmlpath = "/tmp/index.html"
		googlemaps.drawMap(gpxfile,googlekey,htmlpath)
		hfile = wp.newMediaObject(htmlpath)

		description_route = '''<strong>Route: <strong> <br/>
		<iframe width='520' height='480' src='%s'> Need frame support </iframe><br/>
		<a href='%s'>Gpx file</a><br/><br/>''' %(hfile,gfile)

	configuration = XMLParser(conffile)
	ddbb = DDBB(configuration)
	ddbb.connect()
	recordinfo = ddbb.select("records,sports",
		"sports.name,date,distance,time,beats,comments,average,calories,id_record,title,upositive,unegative",
		"id_record=\"%s\" and records.sport=sports.id_sports" %idrecord)
	recordinfo = recordinfo[0]
	title = recordinfo[9]
	sport = recordinfo[0]
	date = recordinfo[1]
	distance = recordinfo[2]
	time = recordinfo[3]
	beats = recordinfo[4]
	comments = recordinfo[5]
	average = recordinfo[6]
	calories = recordinfo[7]
	upositive = recordinfo[10]
	unegative = recordinfo[11]
	
	description_content = comments
	
	description_average = '''
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
''' %(sport,date,distance,time,calories,average,upositive,unegative)

	description_foot = ''' <center>Powered by <a href='http://pytrainer.e-oss.net'>Pytrainer</a></center>'''
	wp.selectBlog(0)
	
	# create post object
	post = wordpresslib.WordPressPost()
	post.title = title
	post.description = description_content+description_average+description_route+description_foot
	post.categories = (['Rutas'])
	
	#pubblish post
	idNewPost = wp.newPost(post, False)
	return "The post has been submited" 
	
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

print main(options)
