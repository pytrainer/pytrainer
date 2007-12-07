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
import xml.dom.minidom 
import time

class Gpx:
	def __init__(self, data_path = None, filename = None):
		self.data_path = data_path
		self.filename = filename
		self.conf = checkConf()
		self.total_dist = 0
		self.total_time = 0
		self.upositive = 0
		self.unegative = 0
		self._getValues()

	def getMaxValues(self):
		return self.total_dist, self.total_time

	def getTrackRoutes(self):	
		dom = xml.dom.minidom.parse(self.filename)
		trks = dom.getElementsByTagName("trk")
		retorno = []
		for trk in trks:
			name = trk.getElementsByTagName("name")[0].firstChild.data
			time_ = trk.getElementsByTagName("time")[0].firstChild.data
			mk_time = time.strptime(time_, "%Y-%m-%dT%H:%M:%SZ")
			time_ = time.mktime(mk_time)
			retorno.append((name,time_))
		return retorno
		
	def getUnevenness(self):
		return self.upositive,self.unegative 
	
	def getTrackList(self):
		return self._getValues()
		
	def _getValues(self):
		dom = xml.dom.minidom.parse(self.filename)
		trkpoints = dom.getElementsByTagName("trkpt")

		retorno = []
		his_vel = []
		last_lat = "False"
		last_lon = "False"
		last_time = "False"
		total_dist = 0
		tmp_alt = 0

		for trkpoint in trkpoints:
			lat = trkpoint.attributes["lat"].value
			lon = trkpoint.attributes["lon"].value
			time_ = trkpoint.getElementsByTagName("time")[0].firstChild.data
			mk_time = time.strptime(time_, "%Y-%m-%dT%H:%M:%SZ")
			time_ = time.mktime(mk_time)
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
					tempnum=(math.sin(last_lat)*math.sin(tmp_lat))+(math.cos(last_lat)*math.cos(tmp_lat)*math.cos(tmp_lon-last_lon))
					try:
						#Obtenemos el punto respecto al punto anterior
						dist=math.acos(tempnum)*111.302*57.29577951
						total_dist += dist
						#dividimos kilometros por hora (no por segundo)
						tmp_vel = dist/((time_)/3600.0)
						vel,his_vel = self._calculate_velocity(tmp_vel,his_vel)
						#si la velocidad es menor de 90 lo damos por bueno
						if vel<90 and time_ <100:
							self.total_time += time_
							retorno.append((total_dist,tmp_alt, self.total_time,vel,lat,lon))
							rel_alt = tmp_alt - last_alt
							if rel_alt > 0:
								self.upositive += rel_alt
							elif rel_alt < 0:
								self.unegative -= rel_alt
					except:
						print tempnum
				
				last_lat = tmp_lat
				last_lon = tmp_lon
				last_alt = tmp_alt
				last_time = tmp_time

		self.total_dist = total_dist 
		return retorno
	
	def _calculate_velocity(self,velocity, arr_velocity):
		arr_velocity.append(velocity)
		if len(arr_velocity)>3:
			arr_velocity.pop(0)
		if len(arr_velocity)<3:
			vel=0
		else:
			vel = (arr_velocity[0]+arr_velocity[1]+arr_velocity[2])/3
		return vel,arr_velocity
