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

class Gpx:
	def __init__(self, data_path = None, filename = None):
		self.data_path = data_path
		self.filename = filename
		self.conf = checkConf()
		self.total_dist = 0
		self.total_time = 0
		self.upositive = 0
		self.unegative = 0
		pytrainerfile = self.gpx2pytrainer()
		self._getValues(pytrainerfile)

	def getMaxValues(self):
		return self.total_dist, self.total_time

	def getDatevalues(self):	
		pytrainerfile = self.gpx2pytrainer()
		fh = open(pytrainerfile)
		line = fh.readline()
		init_time = ""
		i=0
		while line:
			line_arr = re.match("([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*)$",line)
			tmp_time = int(line_arr.group(4))
			if i == 1:
				init_time = tmp_time
			line = fh.readline()
			i = i+1
		end_time = tmp_time
		return init_time, end_time
		
	def getUnevenness(self):
		return self.upositive,self.unegative 
	
	def getTrackList(self):
		pytrainerfile = self.gpx2pytrainer()
		return self._getValues(pytrainerfile)
		
	def gpx2pytrainer(self):
		stylefile = self.data_path+"pytrainer.style"
		tmpfile = self.conf.getValue("tmpdir")+"/gps.txt"
		#os.system("gpsbabel -t -i gpx -f '%s' -x position,distance=10m -o xcsv,style=%s -F %s" %(self.filename, stylefile,tmpfile))
		os.system("gpsbabel -t -i gpx -f '%s' -o xcsv,style=%s -F %s" %(self.filename, stylefile,tmpfile))
		return tmpfile

	def _getValues(self,pytrainerfile):
		fh = open(pytrainerfile)
		retorno = []

		last_lat = "False"
		last_lon = "False"
		last_time = "False"
		his_vel = []
		total_dist = 0

		line = fh.readline()
		
		tmp_alt = 0

		while line:
			line_arr = re.match("([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*)$",line)
			if len(line_arr.group(3)) < 15:
				tmp_alt = int(line_arr.group(3))
	
			#evitamos los puntos blancos
			if (float(line_arr.group(1)) < -0.001) or (float(line_arr.group(1)) > 0.0000001):
				tmp_lat = float(line_arr.group(1))*0.01745329252
				tmp_lon = float(line_arr.group(2))*0.01745329252
				tmp_time = int(line_arr.group(4))
		
				#Para las vueltas diferentes a la primera	
				if last_lat != "False":
					time = tmp_time - last_time
					tempnum=(math.sin(last_lat)*math.sin(tmp_lat))+(math.cos(last_lat)*math.cos(tmp_lat)*math.cos(tmp_lon-last_lon))
					try:
						#Obtenemos el punto respecto al punto anterior
						dist=math.acos(tempnum)*111.302*57.29577951
						total_dist += dist
						#dividimos kilometros por hora (no por segundo)
						tmp_vel = dist/((time)/3600.0)
						vel,his_vel = self._calculate_velocity(tmp_vel,his_vel)
						#si la velocidad es menor de 90 lo damos por bueno
						if vel<90 and time <100:
							self.total_time += time
							retorno.append((total_dist,tmp_alt, self.total_time,vel,line_arr.group(1),line_arr.group(2)))
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
			line = fh.readline()

		fh.close
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
