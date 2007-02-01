#!/usr/bin/python

import sys
import string
import math
import re

numline=0
file = sys.argv[1]
fh = open(file)

fh2 = open("./medicion.txt","w")

last_lat = "False"
last_lon = "False"
last_time = "False"
total_dist = 0

line = fh.readline()
total_time = 0

while line:
	#line_arr = string.split(line," ")
	line_arr = re.match(" ([^ ]*)[^\d-]*([^ ]*)[^\d-]*([^ ]*) ([^\n]*) ",line)
	if len(line_arr.group(3)) < 15:
		tmp_alt = int(line_arr.group(3))
	
	tmp_time = int(line_arr.group(4))
	if last_time != "False":
		time = tmp_time - last_time
		if time < 60:
			total_time += time
		else:
			total_time += 13
	
	#evitamos los puntos blancos
	if (float(line_arr.group(1)) < -0.001) or (float(line_arr.group(1)) > 0.0000001):
		tmp_lat = float(line_arr.group(1))*0.01745329252
		tmp_lon = float(line_arr.group(2))*0.01745329252

		if last_lat != "False":
			tempnum=(math.sin(last_lat)*math.sin(tmp_lat))+(math.cos(last_lat)*math.cos(tmp_lat)*math.cos(tmp_lon-last_lon))
			try:
				dist=math.acos(tempnum)*111.302*57.29577951
				total_dist += dist
				linewrite = "%f %d %s\n" %(total_dist,tmp_alt, total_time)
				linewrite =linewrite.replace(".",",")
				fh2.write(linewrite)
				#print "escribimos"
				#write(fh2,"%f %f" %(total_dist,tmp_alt))
			except:
				print tempnum
		last_lat = tmp_lat
		last_lon = tmp_lon
		
	last_time = tmp_time
	line = fh.readline()

fh.close
fh2.close
	
