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

from lib.ddbb import DDBB
#from lib.system import checkConf
#from lib.xmlUtils import XMLParser

import logging

class Waypoint:
	def __init__(self, data_path = None, parent = None):
		logging.debug(">>")
		self.parent = parent
		self.pytrainer_main = parent
		self.data_path = data_path
		logging.debug("<<")
	
	def removeWaypoint(self,id_waypoint):
		logging.debug(">>")
		#self.pytrainer_main.ddbb.connect()
		logging.debug("Deleting id_waypoint=%s" %id_waypoint)
		self.pytrainer_main.ddbb.delete("waypoints", "id_waypoint=\"%s\"" %id_waypoint)
		#self.pytrainer_main.ddbb.disconnect()
		logging.debug("<<")

	def updateWaypoint(self,id_waypoint,lat,lon,name,desc,sym):
		logging.debug(">>")
		#self.pytrainer_main.ddbb.connect()
		logging.debug("Updating waypoint id: %d with lat %s,lon %s,comment %s,name %s,sym %s" %(id_waypoint,lat,lon,desc,name,sym) )
		self.pytrainer_main.ddbb.update("waypoints","lat,lon,comment,name,sym",[lat,lon,desc,name,sym]," id_waypoint=%d" %id_waypoint)
		#self.pytrainer_main.ddbb.disconnect()
		logging.debug("<<")
		
	def addWaypoint(self,lon=None,lat=None,name=None,comment=None,sym=None): 
		logging.debug(">>") 
		#self.pytrainer_main.ddbb.connect() 
		cells = "lat,lon,comment,name,sym" 
		values = (lat,lon,comment,name,sym) 
		logging.debug("Adding waypoint with details lat %s,lon %s,comment %s,name %s,sym %s" % (lat,lon,comment,name,sym)  )
		self.pytrainer_main.ddbb.insert("waypoints",cells,values) 
		id_waypoint = self.pytrainer_main.ddbb.lastRecord("waypoints") 
		#self.pytrainer_main.ddbb.disconnect() 
		logging.debug("<<") 
		return id_waypoint

	def getwaypointInfo(self,id_waypoint):
		logging.debug(">>")
		#self.pytrainer_main.ddbb.connect()
		retorno = self.pytrainer_main.ddbb.select("waypoints",
					"lat,lon,ele,comment,time,name,sym",
					"id_waypoint=\"%s\"" %id_waypoint)
		#self.pytrainer_main.ddbb.disconnect()
		logging.debug("<<")
		return retorno
	
	def getAllWaypoints(self):
		logging.debug(">>")
		#self.pytrainer_main.ddbb.connect()
		retorno = self.pytrainer_main.ddbb.select("waypoints","id_waypoint,lat,lon,ele,comment,time,name,sym","1=1 order by name")
		#self.pytrainer_main.ddbb.disconnect()
		logging.debug("<<")
		return retorno
	
	def actualize_fromgpx(self,gpxfile):
		logging.debug(">>")
		#self.pytrainer_main.ddbb.connect()
		from lib.gpx import Gpx
		gpx = Gpx(self.data_path,gpxfile)
		tracks = gpx.getTrackRoutes()

		if len(tracks) > 1:
			time = self.date.unixtime2date(tracks[0][1])
			self.recordwindow.rcd_date.set_text(time)
			self._actualize_fromgpx(gpx)
		else:
			msg = _("The gpx file seems to be a several days records. Perhaps you will need to edit your gpx file")
			from gui.warning import Warning
			warning = Warning(self.data_path,self._actualize_fromgpx,[gpx])
                        warning.set_text(msg)
                        warning.run()
		#self.pytrainer_main.ddbb.disconnect()
		logging.debug("<<")

	def _actualize_fromgpx(self, gpx):
		logging.debug(">>")
		distance, time = gpx.getMaxValues()
		upositive,unegative = gpx.getUnevenness()
		self.recordwindow.rcd_upositive.set_text(str(upositive))
		self.recordwindow.rcd_unegative.set_text(str(unegative))
		self.recordwindow.set_distance(distance)
		self.recordwindow.set_recordtime(time/60.0/60.0)
		self.recordwindow.on_calcaverage_clicked(None)
		logging.debug("<<")
