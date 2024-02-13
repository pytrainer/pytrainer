# -*- coding: utf-8 -*-

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

import logging
from pytrainer.lib.date import unixtime2date
from sqlalchemy import Column, Unicode, Float, Integer, Date, select
from pytrainer.lib.ddbb import DeclarativeBase, DDBB


class Waypoint(DeclarativeBase):
    __tablename__ = 'waypoints'
    comment = Column(Unicode(length=240))
    ele = Column(Float)
    id = Column('id_waypoint', Integer, primary_key=True)
    lat = Column(Float)
    lon = Column(Float)
    name = Column(Unicode(length=200))
    sym = Column(Unicode(length=200))
    time = Column(Date)


class WaypointService:

    def __init__(self, data_path = None):
        logging.debug(">>")
        self.ddbb = DDBB()
        self.data_path = data_path
        logging.debug("<<")

    def removeWaypoint(self,id_waypoint):
        logging.debug(">>")
        logging.debug("Deleting id_waypoint=%s", id_waypoint)
        with self.ddbb.sessionmaker.begin() as session:
            waypoint = session.query(Waypoint).filter(Waypoint.id == id_waypoint).one()
            session.delete(waypoint)
        logging.debug("<<")

    def updateWaypoint(self,id_waypoint,lat,lon,name,desc,sym):
        logging.debug(">>")
        logging.debug("Updating waypoint id: %d with lat %s,lon %s,comment %s,name %s,sym %s", id_waypoint, lat, lon, desc, name, sym)
        with self.ddbb.sessionmaker.begin() as session:
            waypoint = session.query(Waypoint).filter(Waypoint.id == id_waypoint).one()
            waypoint.lat = lat
            waypoint.lon = lon
            waypoint.name = name
            waypoint.comment = desc
            waypoint.sym = sym
        logging.debug("<<")

    def addWaypoint(self,lon=None,lat=None,name=None,comment=None,sym=None):
        logging.debug(">>")
        with self.ddbb.sessionmaker.begin() as session:
            waypoint = Waypoint(lon=lon, lat=lat, name=name, comment=comment, sym=sym)
            logging.debug("Adding waypoint with details lat %s,lon %s,comment %s,name %s,sym %s", lat, lon, comment, name, sym)
            session.add(waypoint)
            session.flush()
            waypoint_id = waypoint.id
        logging.debug("<<")
        return waypoint_id

    def getwaypointInfo(self, id_waypoint):
        with self.ddbb.sessionmaker.begin() as session:
            return session.execute(
                select(
                    Waypoint.lat,
                    Waypoint.lon,
                    Waypoint.ele,
                    Waypoint.comment,
                    Waypoint.time,
                    Waypoint.name,
                    Waypoint.sym,
                ).where(Waypoint.id == id_waypoint)).all()

    def getAllWaypoints(self):
        with self.ddbb.sessionmaker.begin() as session:
            return session.execute(
                select(
                    Waypoint.id,
                    Waypoint.lat,
                    Waypoint.lon,
                    Waypoint.ele,
                    Waypoint.comment,
                    Waypoint.time,
                    Waypoint.name,
                    Waypoint.sym,
                ).order_by(Waypoint.name)).all()

    def actualize_fromgpx(self,gpxfile):
        logging.debug(">>")
        from .lib.gpx import Gpx
        gpx = Gpx(self.data_path,gpxfile)
        tracks = gpx.getTrackRoutes()

        if len(tracks) > 1:
            time = unixtime2date(tracks[0][1])
            self.recordwindow.rcd_date.set_text(time)
            self._actualize_fromgpx(gpx)
        else:
            msg = _("The gpx file seems to be a several days records. Perhaps you will need to edit your gpx file")
            from .gui.warning import Warning
            warning = Warning(self.data_path,self._actualize_fromgpx,[gpx])
            warning.set_text(msg)
            warning.run()
        logging.debug("<<")

    def _actualize_fromgpx(self, gpx):
        logging.debug(">>")
        distance, time = gpx.getMaxValues()
        upositive,unegative = gpx.getUnevenness()
        self.recordwindow.rcd_upositive.set_text(str(upositive))
        self.recordwindow.rcd_unegative.set_text(str(unegative))
        self.recordwindow.set_distance(distance)
        self.recordwindow.set_recordtime(time/60.0/60.0)
        self.recordwindow.on_calcavs_clicked(None)
        logging.debug("<<")
