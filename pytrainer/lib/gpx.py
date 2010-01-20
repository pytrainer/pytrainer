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
from datetime import datetime
import logging
from xmlUtils import XMLParser
from lxml import etree
from pytrainer.lib.date import Date

# use of namespaces is mandatory if defined
mainNS = string.Template(".//{http://www.topografix.com/GPX/1/1}$tag")
timeTag = mainNS.substitute(tag="time")
trackTag = mainNS.substitute(tag="trk")
trackPointTag = mainNS.substitute(tag="trkpt")
trackPointTagLast = mainNS.substitute(tag="trkpt[last()]")
trackSegTag = mainNS.substitute(tag="trkseg")
elevationTag = mainNS.substitute(tag="ele")
nameTag = mainNS.substitute(tag="name")

gpxdataNS = string.Template(".//{http://www.cluetrust.com/XML/GPXDATA/1/0}$tag")
calorieTag = gpxdataNS.substitute(tag="calories")
hrTag = gpxdataNS.substitute(tag="hr")
cadTag = gpxdataNS.substitute(tag="cadence")
lapTag = gpxdataNS.substitute(tag="lap")
endPointTag = gpxdataNS.substitute(tag="endPoint")
elapsedTimeTag = gpxdataNS.substitute(tag="elapsedTime")
distanceTag = gpxdataNS.substitute(tag="distance")

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
		#self.Date = Date()
		self.calories= 0
		if filename != None:
			if not os.path.isfile(self.filename):
				return None
			logging.debug("parsing content from "+self.filename)
			self.tree = etree.ElementTree(file=filename).getroot()
			logging.debug("getting values...")
			self.Values = self._getValues()
		logging.debug("<<")

	def getMaxValues(self):
		return self.total_dist, self.total_time, self.maxvel, self.maxhr
	
	def getDate(self):
		return self.date

	def getTrackRoutes(self):	
		trks = self.tree.findall(trackTag)
		tracks = []
		retorno = []
		for trk in trks:
			nameResult = trk.find(nameTag)
			if nameResult is not None:
				name = nameResult.text
			else:
				name = _("No Name")
			timeResult = trk.find(timeTag)
			if timeResult is not None:
				time_ = timeResult.text # check timezone
				mk_time = self.getDateTime(time_)[0]
				time_ = mk_time.strftime("%Y-%m-%d")
			else:
				time_ = _("No Data")
			logging.debug("name: "+name+" | time: "+time_)
			tracks.append((name,time_))
		return tracks

	def getDateTime(self, time_):
		return Date().getDateTime(time_)
		
	def getUnevenness(self):
		return self.upositive,self.unegative 
	
	def getTrackList(self):
		return self.Values

	def getHeartRateAverage(self):
		return self.hr_average

	def getCalories(self):
		return self.calories

	def getLaps(self):
		logging.debug(">>")
		lapInfo = []
		tree  = self.tree
		#date = tree.findtext(timeTag)
		#startTime = self.getDateTime(date)
		laps = tree.findall(lapTag)
		for lap in laps:
			endPoint = lap.find(endPointTag)
			lat = endPoint.get("lat")
			lon = endPoint.get("lon")
			elapsedTime = lap.findtext(elapsedTimeTag)
			if elapsedTime.count(":") == 2: # got a 0:41:42.14 type elasped time
				hours, mins, secs = elapsedTime.split(":")
				elapsedTime = (int(hours) *3600) + (int(mins) * 60) + float(secs)
				#print elapsedTime
			calories = lap.findtext(calorieTag)
			distance = lap.findtext(distanceTag)
			logging.debug("Found time: %s, lat: %s lon: %s cal: %s dist: %s " % (elapsedTime, lat, lon, calories, distance))
			lapInfo.append((elapsedTime, lat, lon, calories, distance))
		return lapInfo
	
	def _getValues(self): 
		'''
		Migrated to eTree XML processing 26 Nov 2009 - jblance
		'''
		logging.debug(">>")
		tree  = self.tree
		# Calories data comes within laps. Maybe more than one, adding them together - dgranda 20100114
		laps = tree.findall(lapTag)
		for lap in laps:
			lapCalories = lap.findtext(calorieTag)
			logging.debug("Lap calories: "+str(lapCalories))
			self.calories += int(lapCalories)
		logging.debug("Calories: "+str(self.calories))

		retorno = []
		his_vel = []
		last_lat = "False"
		last_lon = "False"
		last_time = "False"
		total_dist = 0
		total_hr = 0
		tmp_alt = 0
		len_validhrpoints = 0

		trkpoints = tree.findall(trackPointTag)
		if not len(trkpoints):
			return retorno
		
		date_ = tree.find(timeTag).text
		#mk_time = self.getDateTime(date_)[0] #UTC Date
		mk_time = self.getDateTime(date_)[1] #Local Date
		self.date = mk_time.strftime("%Y-%m-%d")

		for trkpoint in trkpoints:
			lat = trkpoint.get("lat")
			lon = trkpoint.get("lon")
			if lat is None or lat == "" or lon is None or lon == "":
				continue
			#get the heart rate value from the gpx extended format file
			hrResult = trkpoint.find(hrTag)
			if hrResult is not None:
				hr = int(hrResult.text)
				len_validhrpoints += 1
			else: 
				hr = 0
			#get the cadence (if present)
			cadResult = trkpoint.find(cadTag)
			if cadResult is not None:				
				cadence = int(cadResult.text)
			else:
				cadence = 0
			#get the time
			timeResult = trkpoint.find(timeTag)
			if timeResult is not None:
				date_ = timeResult.text
				mk_time = self.getDateTime(date_)[0]
				time_ = time.mktime(mk_time.timetuple()) #Convert date to seconds
			else:
				time_ = 1
			#get the elevation
			eleResult = trkpoint.find(elevationTag)
			if eleResult is not None:
				ele = eleResult.text
			else: 
				ele = None
			#chequeamos que la altura sea correcta / check that the height is correct
			if ele is not None:
				if len(ele)<15:
					tmp_alt = int(float(ele)) #Why convert to int? ele are like "156.3515625"	
				else:
					print "ele len >= 15" + ele
			else:
				tmp_alt= 0
				#print "tmp_alt:" + str(tmp_alt)
			
			#evitamos los puntos blancos / we avoid the white points
			if (float(lat) < -0.000001) or (float(lat) > 0.0000001):
				#Convert lat and lon from degrees to radians
				tmp_lat = float(lat)*0.01745329252  #0.01745329252 = number of radians in a degree
				tmp_lon = float(lon)*0.01745329252  #57.29577951 = 1/0.01745329252 or degrees per radian
				tmp_time = int(time_)
		
				#Para las vueltas diferentes a la primera / For the returns different from first	
				if last_lat != "False":
					time_ = tmp_time - last_time
					if time_>0:
						#Caqlculate diference betwen last and new point
						#tempnum=(math.sin(last_lat)*math.sin(tmp_lat))+(math.cos(last_lat)*math.cos(tmp_lat)*math.cos(tmp_lon-last_lon))
						#try:
						#Pasamos la distancia de radianes a metros..  creo / We convert the distance from radians to meters
						#David no me mates que esto lo escribi hace anhos / Do not kill me this was written ages ago
						#http://faculty.washington.edu/blewis/ocn499/EXER04.htm equation for the distance between 2 points on a spherical earth
						try:
							#dist=math.acos(tempnum)*111.302*57.29577951
							dist=math.acos((math.sin(last_lat)*math.sin(tmp_lat))+(math.cos(last_lat)*math.cos(tmp_lat)*math.cos(tmp_lon-last_lon)))*111.302*57.29577951
						except:
							dist=0
						total_dist += dist
						total_hr += hr
						if hr>self.maxhr:
							self.maxhr = hr
						#dividimos kilometros por hora (no por segundo) / Calculate kilometers per hour (not including seconds)
						tmp_vel = dist/((time_)/3600.0)
						vel,his_vel = self._calculate_velocity(tmp_vel,his_vel, 3)
						#si la velocidad es menor de 90 lo damos por bueno / if speed is greater than 90 or time greater than 100 we exclude the result
						if vel<90 and time_ <100:
							if vel>self.maxvel:
								self.maxvel=vel
							self.total_time += time_
							retorno.append((total_dist,tmp_alt, self.total_time,vel,lat,lon,hr,cadence))
							rel_alt = tmp_alt - last_alt #Could allow for some 'jitter' in height here
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
	
	def _calculate_velocity(self,velocity, arr_velocity, numToAverage): #TODO Check & make generic
		'''Function to calculate moving average for speed'''
		arr_velocity.append(velocity)
		if len(arr_velocity)>numToAverage:
			arr_velocity.pop(0)
		if len(arr_velocity)<numToAverage:
			#Got too few numbers to average
			#Pad with duplicates
			for x in range(len(arr_velocity), numToAverage):
				arr_velocity.append(velocity)
		vel = 0
		for v in arr_velocity:
			vel+= v
		vel /= numToAverage
		return vel,arr_velocity
		
	def getStartTimeFromGPX(self, gpxFile):
		"""03.05.2008 - dgranda
		Retrieves start time from a given gpx file 
		args:
			- gpxFile: path to xml file (gpx format)
		returns: string with start time - 2008-03-22T12:17:43Z
		"""
		logging.debug(">>")
		date_time = self.tree.find(timeTag) #returns first instance found
		if date_time is None:
			print "Problems when retrieving start time from "+gpxFile+". Please check data integrity"
			return 0
		dateTime = self.getDateTime(date_time.text)
		zuluDateTime = dateTime[0].strftime("%Y-%m-%dT%H:%M:%SZ")
		localDateTime = dateTime[1]
		logging.debug(gpxFile+" | "+ date_time.text +" | " + zuluDateTime)
		#print localDateTime
		#return date_time.text
		logging.debug("<<")
		return (zuluDateTime, localDateTime)

