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

	def getMaxValues(self):
		pytrainerfile = self.gpx2pytrainer()
		val = self._getValues(pytrainerfile)
		total_dist = val[-1][0]
		total_time = val[-1][2]
		return total_dist, total_time

	def getDatevalues(self):	
		pytrainerfile = self.gpx2pytrainer()
		fh = open(pytrainerfile)
		line = fh.readline()
		init_time = ""
		while line:
			line_arr = re.match("([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*)$",line)
			tmp_time = int(line_arr.group(4))
			if init_time == "":
				init_time = tmp_time
			line = fh.readline()
		end_time = tmp_time
		return init_time, end_time
	
	def getTrackList(self):
		pytrainerfile = self.gpx2pytrainer()
		return self._getValues(pytrainerfile)
		
	def gpx2pytrainer(self):
		stylefile = self.data_path+"pytrainer.style"
		tmpfile = self.conf.getValue("tmpdir")+"/gps.txt"
		os.system("gpsbabel -t -i gpx -f %s -x position,distance=1m -o xcsv,style=%s -F %s" %(self.filename, stylefile,tmpfile))
		return tmpfile

	def _getValues(self,pytrainerfile):
		numline=0
		fh = open(pytrainerfile)
		#fh2 = open("/tmp/medicion.txt","w")
		retorno = []

		last_lat = "False"
		last_lon = "False"
		last_time = "False"
		his_vel = []
		total_dist = 0

		line = fh.readline()
		total_time = 0
		tmp_total_time = 0

		while line:
			#line_arr = re.match("([^ ]*)[^\d-]*([^ ]*)[^\d-]*([^ ]*) ([^\n]*) ",line)
			line_arr = re.match("([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*)$",line)
			if len(line_arr.group(3)) < 15:
				tmp_alt = int(line_arr.group(3))
	
	
			#evitamos los puntos blancos
			if (float(line_arr.group(1)) < -0.001) or (float(line_arr.group(1)) > 0.0000001):
				tmp_lat = float(line_arr.group(1))*0.01745329252
				tmp_lon = float(line_arr.group(2))*0.01745329252
				tmp_time = int(line_arr.group(4))

				if last_lat != "False":
					time = tmp_time - last_time
					total_time += time
					tempnum=(math.sin(last_lat)*math.sin(tmp_lat))+(math.cos(last_lat)*math.cos(tmp_lat)*math.cos(tmp_lon-last_lon))
					try:
						dist=math.acos(tempnum)*111.302*57.29577951
						total_dist += dist
						#dividimos kilometros por hora (no por segundo)
						tmp_vel = dist/((time)/3600.0)
						his_vel.append(tmp_vel)
						if len(his_vel)>3:
							his_vel.pop(0)
						if len(his_vel)<3:
							vel=0
						else:
							vel = (his_vel[0]+his_vel[1]+his_vel[2])/3
						if vel<80:
							retorno.append((total_dist,tmp_alt, total_time,vel))
					except:
						print tempnum
				
				last_lat = tmp_lat
				last_lon = tmp_lon
				last_time = tmp_time
				tmp_total_time = total_time
			line = fh.readline()

		fh.close
		return retorno
	
