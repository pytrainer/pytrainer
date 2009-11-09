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


import os
import commands

class googleearth():
	def __init__(self, parent = None):
		self.parent = parent
		self.tmpdir = self.parent.conf.getValue("tmpdir")

	def run(self):
		f = os.popen("zenity --file-selection --title 'Choose a Google Earth file (.kml) to import'")
		inputData = f.read().strip()

		tmpgpx="/tmp/reg.gpx"
		outgps = commands.getstatusoutput("gpsbabel -t -i kml -f %s -o gpx -F %s" % (inputData, tmpgpx) )

		return [tmpgpx, ]

