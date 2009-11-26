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
	def __init__(self, vbox = None, window = None, combovalue = None, combovalue2 = None):
		self.drawarea = DrawArea(vbox, window)
		self.combovalue = combovalue
		self.combovalue2 = combovalue2

	def drawgraph(self,values, date_ini, date_end):
		logging.debug(">>")
		value_selected = self.combovalue.get_active()
		if value_selected < 0:
			self.combovalue.set_active(0)
			value_selected = 0
		value_selected2 = self.combovalue2.get_active()
		if value_selected2 < 0:
			self.combovalue2.set_active(0)
			value_selected2 = 0
		logging.debug(str(values))
		ylabel,title = self.get_value_params(value_selected)
		xlabel = ""
		#build days list to ensure localised values are used.
		days = []
		for day in range(0, 7):
			dateTemp = datetime.datetime.strptime(date_ini, "%Y-%m-%d")
			incrementDay = datetime.timedelta(days=day)
			dateToUse = dateTemp + incrementDay
			days.append( unicode(dateToUse.strftime("%a")) )

		valueDict = {} #Stores the totals
		valueCount = {} #Counts the totals to allow for averaging if needed

		for record in values:
			day = datetime.datetime.strptime(record[0], "%Y-%m-%d").strftime("%a") # Gives Sun, Mon etc for this record
			sport = record[9]
			value = self.getValue(record, value_selected)
			if sport in valueDict: #Already got this sport
				if day in valueDict[sport]: #Already got this sport on this day
					valueDict[sport][day] += value
					valueCount[sport][day] += 1
				else: #New day for this sport
					valueDict[sport][day] = value
					valueCount[sport][day] = 1
			else: #New sport
				valueDict[sport] = {day: value}
				valueCount[sport] = {day: 1}

		if value_selected == 2 or value_selected == 3:
			for sport in valueDict.keys():
				for day in valueDict[sport].keys():
					logging.debug("averaging values: before %s (count %s)" % (valueDict[sport][day],valueCount[sport][day]))
					if valueCount[sport][day] > 1: #Only average if 2 or more entries on this day
						valueDict[sport][day] /= valueCount[sport][day]
					logging.debug("averaging values: after %s" % valueDict[sport][day])

		self.drawarea.drawStackedBars(days,valueDict,xlabel,ylabel,title)
		logging.debug("<<")

	def get_value_params(self,value):
		if value == 0:
			return _("Kilometers"),_("Weekly kilometers")
		elif value == 1:
			return _("Time in Hours"), _("Weekly Time")
		elif value == 2:
			return _("Beats per Minute"), _("weekly Beats")
		elif value == 3:
			return _("Average Speed (km/h)"), _("Weekly Speed Averages")
		elif value == 4:
			return _("Calories"), _("Weekly Calories")

	def getValue(self,record,value_selected):
		#hacemos una relacion entre el value_selected y los values / we make a relation between value_selected and the values
		conv = {
			0: 1, #value 0 es kilometros (1)
			1: 2, #value 1 es tiempo (2)
			2: 3, #value 2 es pulsaciones(3)
			3: 5, #value 3 es media(5)
			4: 6 #value 4 es calorias(6)
			}
		value_sel = conv[value_selected]
		#si la opcion es tiempo lo pasamos a horas / if the option is time we passed it to hours
		if (value_sel == 2):
			return self.getFloatValue(record[value_sel])/3600
		else:
			return self.getFloatValue(record[value_sel])
	
	def getFloatValue(self, value):
		try:
			return float(value)
		except:
			return float(0)



