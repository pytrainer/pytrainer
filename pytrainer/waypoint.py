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
from lib.system import checkConf
from lib.xmlUtils import XMLParser

class Waypoint:
	def __init__(self, data_path = None, parent = None):
		self.parent = parent
		self.data_path = data_path
		self.conf = checkConf()
		self.filename = self.conf.getValue("conffile")
		self.configuration = XMLParser(self.filename)
		self.ddbb = DDBB(self.configuration)
		self.ddbb.connect()
	
	def removeWaypoint(self,id_waypoint):
		self.ddbb.delete("waypoints", "id_waypoint=\"%s\"" %id_waypoint)

	def updateWaypoint(self,id_waypoint,lat,lon,name,desc):
		self.ddbb.update("waypoints","lat,lon,comment,name",[lat,lon,desc,name]," id_waypoint=%d" %id_waypoint)

	def getwaypointInfo(self,id_waypoint):
		return self.ddbb.select("waypoint",
					"lat,lon,ele,comment,time,name,sym"
					"id_waypoint=\"%s\"" %id_waypoint)
	
	def getAllWaypoints(self):
		return self.ddbb.select("waypoints","id_waypoint,lat,lon,ele,comment,time,name,sym","1=1 order by name")
	
	def actualize_fromgpx(self,gpxfile):
		from lib.gpx import Gpx
		gpx = Gpx(self.data_path,gpxfile)
		init_time,end_time = gpx.getDatevalues()
		init_time = self.date.unixtime2date(init_time)	
		end_time = self.date.unixtime2date(end_time)
		if init_time == end_time:
			self.recordwindow.rcd_date.set_text(end_time)
			self._actualize_fromgpx(gpx)
		else:
			msg = _("The gpx file seems to be a several days records. Perhaps you will need to edit your gpx file")
			from gui.warning import Warning
			warning = Warning(self.data_path,self._actualize_fromgpx,[gpx])
                        warning.set_text(msg)
                        warning.run()

	def _actualize_fromgpx(self, gpx):
		distance, time = gpx.getMaxValues()
		upositive,unegative = gpx.getUnevenness()
		self.recordwindow.rcd_upositive.set_text(str(upositive))
		self.recordwindow.rcd_unegative.set_text(str(unegative))
		self.recordwindow.set_distance(distance)
		self.recordwindow.set_recordtime(time/60.0/60.0)
		self.recordwindow.on_calcaverage_clicked(None)
		
