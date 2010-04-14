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

from xmlUtils import XMLParser

def getZones(pytrainer_main=None):
	#conf = checkConf()
	#filename = conf.getValue("conffile")
	#configuration = XMLParser(filename)
	maxhr = int(pytrainer_main.profile.getValue("pytraining","prf_maxhr"))
	resthr = int(pytrainer_main.profile.getValue("pytraining","prf_minhr"))

	if pytrainer_main.profile.getValue("pytraining","prf_hrzones_karvonen")=="True":
		#if karvonen method
		targethr1 = ((maxhr - resthr) * 0.50) + resthr
		targethr2 = ((maxhr - resthr) * 0.60) + resthr
		targethr3 = ((maxhr - resthr) * 0.70) + resthr
		targethr4 = ((maxhr - resthr) * 0.80) + resthr
		targethr5 = ((maxhr - resthr) * 0.90) + resthr
		targethr6 = maxhr
	else:
		#if not karvonen method
		targethr1 = maxhr * 0.50
		targethr2 = maxhr * 0.60
		targethr3 = maxhr * 0.70
		targethr4 = maxhr * 0.80
		targethr5 = maxhr * 0.90
		targethr6 = maxhr

	zone1 = (targethr1,targethr2,"#ffff99",_("Moderate activity"))
	zone2 = (targethr2,targethr3,"#ffcc00",_("Weight Control"))
	zone3 = (targethr3,targethr4,"#ff9900",_("Aerobic"))
	zone4 = (targethr4,targethr5,"#ff6600",_("Anaerobic"))
	zone5 = (targethr5,targethr6,"#ff0000",_("VO2 MAX"))

	return zone5,zone4,zone3,zone2,zone1

