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
#from gtrnctr2gpx import gtrnctr2gpx
import os
import commands

parser = OptionParser()
parser.add_option("-d", "--device", dest="device")
(options,args) =  parser.parse_args()
gtrnctrFile="/tmp/file.gtrnctr"
gtrnctrFileMod="/tmp/file_mod.gtrnctr"
input_dev = options.device

# ToDo (19.05.2008): better exception handling
try:
	outmod = commands.getstatusoutput('/sbin/lsmod | grep garmin_gps')
	#os.popen("zenity --error --text='Devuelve: %s'" %str(outmod))
	if outmod[0]==256:	#there is no garmin_gps module loaded
		input_dev = "usb:"
	else:
		raise Exception
	# Can't export to GPX directly because lack of support for heartrate and sports (1.0 version, may change when gpsbabel supports 1.1 with custom fields)
	outgps = commands.getstatusoutput("gpsbabel -t -i garmin -f %s -o gtrnctr -F /tmp/file.gtrnctr | zenity --progress --pulsate --text='Loading Data' auto-close" %input_dev)
	#os.popen("zenity --error --text='Devuelve: %s'" %str(outgps))
	# XML file from gpsbabel refers to schemas and namespace definitions which are no longer available, removing this info - dgg - 12.05.2008
	if outgps[0]==0:
		if outgps[1] == "Found no Garmin USB devices.": # check localizations
			raise Exception
		else:
			if os.path.isfile(gtrnctrFile):
				f = open(gtrnctrFile,"r")
				lines = f.readlines()
				f.close()
				f = open(gtrnctrFileMod,'w')
				headers = lines[0]+'<TrainingCenterDatabase>\n'
				f.write(headers)
				f.write(''.join(lines[6:]))
				f.close()
				print gtrnctrFileMod
	else:
		raise Exception
except Exception:
	os.popen("zenity --error --text='Can not handle Garmin device\nCheck your configuration\nCurrent usb port is set to:\t %s'" %input_dev);

