#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#Copyright (C) DJ dj@namurlug.org   http://blog.dedj.be

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

import xmlrpclib
import SOAPpy
import os
from pytrainer.lib.date import second2time
from pytrainer.lib.soapUtils import *

from optparse import OptionParser


class Main:
	def __init__(self,options):
		# on definit les parametres de connection au blog
		self.xmlrpcserver = options.xmlrpcserver
		self.blogid = options.blogid
		self.user = options.bloguser
		self.password = options.blogpass
		self.category_nbr = options.blogcategory
		#if you want accept comment, replace False by True
		self.comment = False
		#or ping
		self.ping = False
		
		
		self.category = [{'isPrimary': True, "categoryId" : self.category_nbr}]
		
		self.error = ""
		self.log =""
		self.idrecord = options.idrecord
		self.webserviceserver = SOAPpy.SOAPProxy("http://localhost:8081/")

		#we try the connection to the xml/rpc server
		try :
			self.connect = xmlrpclib.Server(self.xmlrpcserver)
			self.error = False
		except : 
			print "can't connect the server"
			
	def loadRecordInfo(self):
      		record = self.webserviceserver.getRecordInfo(self.idrecord)
		self.sport = record["sport"]
                self.date = record["date"]
                self.distance = record["distance"]
                self.time = second2time(float(record["time"]))
                self.heure = self.time[0]
                self.minute = self.time[1] 
                self.seconde = self.time[2]
                self.beats = record["beats"]
                self.comments = record["comments"]
                self.average = record["average"]
                self.calories = record["calories"]
                self.title = record["title"]
                self.upositive = record["upositive"]
                self.unegative = record["unegative"]

	def construction(self):
		#this methode create the content post content, the section between the '''   are on html  thake wath you want
		#self.date, self.distance, self.time, self.beats, self.comments, self.average, self.calories, self.title, self.title, self.upositive, self.unegative, self.sport
		description_table = '''
			<p>%s %s</p>
			<p>With a average of %s km/h</p><br />
			<p>I have lost %s kcalories and my heart have %s pulsations (on average)</p>
			''' %(self.sport, self.title,self.average, self.calories, self.beats)
		return description_table

	def chapeau(self):
		chapeau_table = '''
			<p>A %s score on a distance of %s km on %sh %sm %s </p><br />
			''' %(self.sport,self.distance,self.heure, self.minute, self.seconde)
		return chapeau_table

	def run(self):
		#we load all info for the record
		self.loadRecordInfo()
		blog_desc = self.construction()
		blog_chap = self.chapeau()

		if self.error == False:
			#post_description = "Du " + str(self.sport) + " sur une distance de " + str(self.distance) +"km " + " en " + str(self.time) + " ce qui nous fait une moyenne de " + str(self.average)
			server = xmlrpclib.Server(options.xmlrpcserver)
			content = {'title' : self.date, 'description' : blog_desc, 'mt_allow_comments' : self.comment, 'mt_allow_pings' : self.ping,'mt_excerpt' : blog_chap}
			post = server.metaWeblog.newPost(self.blogid, self.user, self.password, content , True)
			#we change the post categories because, i( or it's the false of xml/rpc) can't select the categories before the upload on the blog 
			change_cat = server.mt.setPostCategories(post,self.user,self.password, self.category)
			return "The post has been submited" 
			self.webserviceserver.stop
        				
		else:
			return self.log


parser = OptionParser()
parser.add_option("-d", "--device", dest="device")
parser.add_option("-k", "--xmlrpcserver", dest="xmlrpcserver")
parser.add_option("-u", "--bloguser", dest="bloguser")
parser.add_option("-p", "--blogpass", dest="blogpass")
parser.add_option("-l", "--blogid", dest="blogid")
parser.add_option("-c", "--blogcategory", dest="blogcategory")
parser.add_option("-g", "--gpxfile", dest="gpxfile")
parser.add_option("-i", "--idrecord", dest="idrecord")
(options,args) =  parser.parse_args()

try : 
  x = Main(options)
  x.run()
  print "le score du %s a ete envoye"  % x.date
except xmlrpclib.Fault, f:
  print "ERROR on the server\n   Code %i\n   Reason %s" % (f.faultCode,
                                               f.faultString)
