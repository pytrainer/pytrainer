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

class WeekGraph:
	def __init__(self, vbox = None, window = None):
		self.drawarea = DrawArea(vbox, window)

	def drawgraph(self,values, date_ini, date_end):
		logging.debug(">>")
		#print "Found %d records" % len(values)
		logging.debug(str(values))
		#build days list to ensure localised values are used.
		days = []
		for day in range(0, 7):
			dateTemp = datetime.datetime.strptime(date_ini, "%Y-%m-%d")
			incrementDay = datetime.timedelta(days=day)
			dateToUse = dateTemp + incrementDay
			days.append( dateToUse.strftime("%a") )
		valueDict = {}
		for record in values:
			day = datetime.datetime.strptime(record[1], "%Y-%m-%d").strftime("%a") # Gives Sun, Mon etc for this record
			sport = record[0]
			distance = record[2]
			if sport in valueDict: #Already got this sport
				if day in valueDict[sport]: #Already got this sport on this day
					valueDict[sport][day] += distance
				else: #New day for this sport
					valueDict[sport][day] = distance
			else: #New sport
				valueDict[sport] = {day: distance}

		xlab = "Day"
		ylab = "kilometers"
		tit = "Week View"
		self.drawarea.stadistics("stackedbars",days,valueDict,xlab,ylab,tit)
		logging.debug("<<")






