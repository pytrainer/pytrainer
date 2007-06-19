# -*- coding: iso-8859-1 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net
# vud1@grupoikusnet.com
# Jakinbidea & Grupo Ikusnet Developer

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

import SOAPpy
from pytrainer.lib.ddbb import DDBB
from pytrainer.lib.xmlUtils import XMLParser

from threading import Thread

#class webService():
class webService(Thread):
	def __init__(self,system):
		self.conffile = "%s/conf.xml" %system.getValue("confdir")
		self.server = SOAPpy.ThreadingSOAPServer(("localhost", 8081))
		#self.server = SOAPpy.server.InsecureServer(("localhost", 8081))
		self.server.registerFunction(self.getRecordInfo)
		Thread.__init__ ( self )

	def getRecordInfo(self,id_record):
		configuration = XMLParser(self.conffile)
		ddbb = DDBB(configuration)
		ddbb.connect()
		recordinfo = ddbb.select("records,sports",
                        "sports.name,date,distance,time,beats,comments,average,calories,id_record,title,upositive,unegative",
                        "id_record=\"%s\" and records.sport=sports.id_sports" %id_record)
		record = recordinfo[0]
		info = {}
		info["sport"] = record[0]
		info["date"] = record[1]
		info["distance"] = record[2]
		info["time"] = record[3]
		info["beats"] = record[4]
		info["comments"] = record[5]
		info["average"] = record[6]
		info["calories"] = record[7]
		info["title"] = record[9]
		info["upositive"] = record[10]
		info["unegative"] = record[11]
		return info

	def addWaypoint(self,point):
		lat = point[0]
		lon = point[1]
		comment = point[2]
		name = point[3]
		sym = point[4]
		
		configuration = XMLParser(self.conffile)
		ddbb = DDBB(configuration)
		ddbb.connect()
		cells = "lat,lon,comment,name,sym"
		values = (lat,lon,comment,name,sym)
		ddbb.insert("waypoints",cells,values)

	def run(self):
		self.server.serve_forever()
			
