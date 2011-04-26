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

from gui.drawArea import DrawArea
import logging
import datetime
import calendar
from timegraph import TimeGraph

class WeekGraph(TimeGraph):

	value_params = [
		(None, _("Distance (km)"),_("Daily Distance"), None),
		(None, _("Time (hours)"), _("Daily Time"), None),
		(None, _("Average Heart Rate (bpm)"), _("Daily Average Heart Rate"), None),
		(None, _("Average Speed (km/h)"), _("Daily Average Speed"), None),
		(None, _("Calories"), _("Daily Calories"), None),
	]

	def __init__(self, vbox = None, window = None, combovalue = None, combovalue2 = None, main = None):
		TimeGraph.__init__(self, vbox=vbox, window=window, main=main)
		self.combovalue = combovalue
		self.combovalue2 = combovalue2
		self.KEY_FORMAT = "%a"

	def drawgraph(self,values, date_ini):
		TimeGraph.drawgraph(self, values, x_func=lambda x: getDays(date_ini))

def getDays(date_ini):
	#TODO look at using calendar.day_abbr for this
	return [(datetime.datetime.strptime(date_ini, "%Y-%m-%d")+datetime.timedelta(x)).strftime("%a") for x in xrange(0,7)]

