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

import sys
import string
import math
import re
import os
from system import checkConf
 
import time
import logging
from xmlUtils import XMLParser
import xml.dom
from xml.dom import minidom, Node, getDOMImplementation
import xml.etree.cElementTree
from gtrnctr2gpx import gtrnctr2gpx # copied to pytrainer/lib/ directory

# use of namespaces is mandatory if defined
mainNS = string.Template("{http://www.topografix.com/GPX/1/1}$tag")
timeTag = mainNS.substitute(tag="time")
trackTag = mainNS.substitute(tag="trk")
trackPointTag = mainNS.substitute(tag="trkpt")

class Gpx:
	def __init__(self, data_path = None, filename = None, trkname = None):
		logging.debug(">>")
		self.data_path = data_path
		self.filename = filename
		self.trkname = trkname
		logging.debug(str(data_path)+"|"+str(filename)+"|"+str(trkname))
		self.conf = checkConf()
		self.total_dist = 0
		self.total_time = 0
		self.upositive = 0
		self.unegative = 0
		self.maxvel = 0
		self.maxhr = 0
		self.date = ""
		self.tracks = []
		if not os.path.isfile(self.filename):
			return None
		self.dom = xml.dom.minidom.parse(self.filename)
		self.Values = self._getValues()

	def getMaxValues(self):
		return self.total_dist, self.total_time, self.maxvel, self.maxhr
	
	def getDate(self):
		return self.date

	def getTrackRoutes(self):	
		return self.tracks
		
	def getUnevenness(self):
		return self.upositive,self.unegative 
	
	def getTrackList(self):
		return self.Values

	def getHeartRateAverage(self):
		return self.hr_average
		
	def _getValues(self):
		logging.debug(">>")
		dom = self.dom
		content = dom.toxml()

		trks = dom.getElementsByTagName("trk")
		retorno = []
		for trk in trks:
			if len(trk.getElementsByTagName("name")) > 0:
				name = trk.getElementsByTagName("name")[0].firstChild.data
			else:
				name = _("No Name")
			if len(trk.getElementsByTagName("time")) > 0:
				time_ = trk.getElementsByTagName("time")[0].firstChild.data
				mk_time = time.strptime(time_, "%Y-%m-%dT%H:%M:%SZ")
				time_ = time.strftime("%Y-%m-%d", mk_time)
			else:
				time_ = _("No Data")
			logging.debug("name: "+name+" | time: "+time_)
			self.tracks.append((name,time_))
			
			name = trk.getElementsByTagName("name")[0].firstChild.data
			if name == self.trkname:
				dom = trk
				content = """<?xml version="1.0" encoding="UTF-8"?>

<gpx 
creator="pytrainer http://pytrainer.e-oss.net"
version="1.1" 
xmlns="http://www.topografix.com/GPX/1/1" 
xmlns:geocache="http://www.groundspeak.com/cache/1/0" 
xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" 
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.cluetrust.com/XML/GPXDATA/1/0 http://www.cluetrust.com/Schemas/gpxdata10.xsd">


"""
				content += dom.toxml()
				content += "</gpx>"

		#Guardamos el xml en un fichero (por si hay que guardar solo un track)					
		newfilename = self.conf.tmpdir+"/newgpx.gpx"
		if os.path.isfile(newfilename):
			os.remove(newfilename)
		fp = open(newfilename,"a+")
		fp.write(content)
		fp.close()

		trkpoints = dom.getElementsByTagName("trkpt")
		retorno = []
		his_vel = []
		last_lat = "False"
		last_lon = "False"
		last_time = "False"
		total_dist = 0
		total_hr = 0
		tmp_alt = 0
		len_validhrpoints = 0
			
		date_ = trkpoints[0].getElementsByTagName("time")[0].firstChild.data
		mk_time = time.strptime(date_, "%Y-%m-%dT%H:%M:%SZ")
		self.date = time.strftime("%Y-%m-%d", mk_time)

		for trkpoint in trkpoints:
			lat = trkpoint.attributes["lat"].value
			lon = trkpoint.attributes["lon"].value
			#get the heart rate value from the gpx extended format file
			if len(trkpoint.getElementsByTagName("gpxdata:hr")) > 0:
				hr = int(trkpoint.getElementsByTagName("gpxdata:hr")[0].firstChild.data)
				len_validhrpoints += 1
			else: 
				hr = 0
			if len(trkpoint.getElementsByTagName("time")) > 0:
				time_ = trkpoint.getElementsByTagName("time")[0].firstChild.data
				mk_time = time.strptime(time_, "%Y-%m-%dT%H:%M:%SZ")
				time_ = time.mktime(mk_time)
			else:
				time_ = 1
			ele = trkpoint.getElementsByTagName("ele")[0].firstChild.data
			#chequeamos que la altura sea correcta
			if len(ele)<15:
				tmp_alt = int(float(ele))
			
			#evitamos los puntos blancos
			if (float(lat) < -0.000001) or (float(lat) > 0.0000001):
				tmp_lat = float(lat)*0.01745329252
				tmp_lon = float(lon)*0.01745329252
				tmp_time = int(time_)
		
				#Para las vueltas diferentes a la primera	
				if last_lat != "False":
					time_ = tmp_time - last_time
					if time_>0:
						tempnum=(math.sin(last_lat)*math.sin(tmp_lat))+(math.cos(last_lat)*math.cos(tmp_lat)*math.cos(tmp_lon-last_lon))
						#try:
						#Obtenemos el punto respecto al punto anterior
						try:
							dist=math.acos(tempnum)*111.302*57.29577951
						except:
							dist=0
						total_dist += dist
						total_hr += hr
						if hr>self.maxhr:
							self.maxhr = hr
						#dividimos kilometros por hora (no por segundo)
						tmp_vel = dist/((time_)/3600.0)
						vel,his_vel = self._calculate_velocity(tmp_vel,his_vel)
						#si la velocidad es menor de 90 lo damos por bueno
						if vel<90 and time_ <100:
							if vel>self.maxvel:
								self.maxvel=vel
							self.total_time += time_
							retorno.append((total_dist,tmp_alt, self.total_time,vel,lat,lon,hr))
							rel_alt = tmp_alt - last_alt
							if rel_alt > 0:
								self.upositive += rel_alt
							elif rel_alt < 0:
								self.unegative -= rel_alt
				
				last_lat = tmp_lat
				last_lon = tmp_lon
				last_alt = tmp_alt
				last_time = tmp_time

		self.hr_average = 0
		if len_validhrpoints > 0:
			self.hr_average = total_hr/len_validhrpoints
		self.total_dist = total_dist
		logging.debug("<<")
		return retorno
	
	def _calculate_velocity(self,velocity, arr_velocity):
		#logging.debug(">>")
		arr_velocity.append(velocity)
		if len(arr_velocity)>3:
			arr_velocity.pop(0)
		if len(arr_velocity)<3:
			vel=0
		else:
			vel = (arr_velocity[0]+arr_velocity[1]+arr_velocity[2])/3
		#logging.debug("<<")
		return vel,arr_velocity
