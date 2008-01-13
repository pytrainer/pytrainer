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


from optparse import OptionParser
from gtrnctr2gpx import gtrnctr2gpx
import os

parser = OptionParser()
parser.add_option("-d", "--device", dest="device")
(options,args) =  parser.parse_args()

tmpgpx = "/tmp/reg.gpx"
dummy = 0


try:
	os.system("gpsbabel -t -i garmin -f %s -o gtrnctr -F /tmp/file.gtrnctr" %options.device)
	dummy = 1
except:
	f = os.popen("zenity --error --text='Cant open garmin device. Check your configuration or connect the device correctly.'");
	dummy = 0

if dummy == 1:
	gtrnctr2gpx("/tmp/file.gtrnctr","/tmp/file.gpx")
	print "/tmp/file.gpx"
else:
	print 0

