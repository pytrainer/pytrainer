#!/usr/bin/python
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

import xml.dom.minidom

#the _variables are the gpx ones. The variables are the xcsv one


def gtrnctr2gpx(gtrnctrfile,gpxfile):
	dom = xml.dom.minidom.parse(gtrnctrfile)
	d = xml.dom.minidom.getDOMImplementation()
	_dom = d.createDocument(None,"gpx",None)
	_gpx_element = _dom.documentElement
	_gpx_element.setAttribute('creator',"pytrainer http://pytrainer.e-oss.net")
	_gpx_element.setAttribute('version',"1.1")
	_gpx_element.setAttribute('xmlns',"http://www.topografix.com/GPX/1/1")
	_gpx_element.setAttribute('xmlns:geocache',"http://www.groundspeak.com/cache/1/0")
	_gpx_element.setAttribute('xmlns:gpxdata',"http://www.cluetrust.com/XML/GPXDATA/1/0")
	_gpx_element.setAttribute('xmlns:xsi',"http://www.w3.org/2001/XMLSchema-instance")
	_gpx_element.setAttribute('xsi:schemaLocation',"http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.cluetrust.com/XML/GPXDATA/1/0 http://www.cluetrust.com/Schemas/gpxdata10.xsd")
	
	trks = dom.getElementsByTagName("Track")
	nametrack = 0
	for trk in trks:
		nametrack = nametrack+1
		_trk = _dom.createElement("trk")
		_name = _dom.createElement("name")
		_name.appendChild(_dom.createTextNode("%s"%str(nametrack)))
		_trk.appendChild(_name)
		trkpoints = trk.getElementsByTagName("Trackpoint")
		for trkpoint in trkpoints:
			_trkpt = _dom.createElement("trkpt")
			time = trkpoint.getElementsByTagName("Time")[0].firstChild.data
			alt = trkpoint.getElementsByTagName("AltitudeMeters")[0].firstChild.data
			hr = trkpoint.getElementsByTagName("HeartRateBpm")[0].firstChild.data
			lat = trkpoint.getElementsByTagName("LatitudeDegrees")[0].firstChild.data
			lon = trkpoint.getElementsByTagName("LongitudeDegrees")[0].firstChild.data
	
			_time = _dom.createElement("time")
			_ele = _dom.createElement("ele")
			_hr = _dom.createElement("gpxdata:hr")
			_extensions = _dom.createElement("extensions")
			_time.appendChild(_dom.createTextNode(time))
			_ele.appendChild(_dom.createTextNode(alt))
			_hr.appendChild(_dom.createTextNode(hr))
			_extensions.appendChild(_hr)
			_trkpt.appendChild(_time)
			_trkpt.appendChild(_ele)
			_trkpt.appendChild(_extensions)
			_trkpt.setAttribute('lat', lat) 
			_trkpt.setAttribute('lon', lon) 
			_trk.appendChild(_trkpt)
		_gpx_element.appendChild(_trk)

	f = open(gpxfile, 'w')		
	_dom.writexml(f)
	f.close()

