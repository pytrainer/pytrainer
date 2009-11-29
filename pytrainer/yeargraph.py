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
import calendar

class YearGraph:
	def __init__(self, vbox = None, window = None, combovalue = None, combovalue2 = None):
		self.drawarea = DrawArea(vbox, window)
		self.combovalue = combovalue
		self.combovalue2 = combovalue2

	def drawgraph(self,values):
		xval = []
		yval = []
		xlab = []
		ylab = []
		tit = []
		col = []
		value_selected = self.combovalue.get_active()
		value_selected2 = self.combovalue2.get_active()
		if value_selected < 0:
			self.combovalue.set_active(0)
			value_selected = 0
		monthsnumber,xlabel,ylabel,title,color = self.get_value_params(value_selected)
		xvalues,yvalues = self.get_values(values,value_selected,monthsnumber)

                xval.append(xvalues)
                yval.append(yvalues)
                if value_selected2 < 0:
                        xlab.append("")
                else:
                        xlab.append(xlabel)
                ylab.append(ylabel)
                tit.append(title)
                col.append(color)

                if value_selected2 < 0:
                        self.combovalue2.set_active(0)
                        value_selected2 = 0
                if value_selected2 > 0:
                        value_selected2 = value_selected2-1
                        daysmonth,xlabel,ylabel,title,color = self.get_value_params(value_selected2)
                        xvalues,yvalues = self.get_values(values,value_selected2,daysmonth)
                        xval.append(xvalues)
                        yval.append(yvalues)
                        xlab.append(xlabel)
                        ylab.append(ylabel)
                        tit.append(title)
                        col.append(color)
		self.drawarea.stadistics("bars",xval,yval,xlab,ylab,tit,col)

	def get_value_params(self,value):
		if value == 0:
			return 12,_("month"),_("Distance (km)"),_("Monthly Distance"),"y"
		elif value == 1:
			return 12,_("month"),_("Time (hours)"), _("Monthly Time"),"b"
		elif value == 2:
			return 12,_("month"),_("Average Heart Rate (bpm)"), _("Monthly Average Heart Rate"),"r"
		elif value == 3:
			return 12,_("month"),_("Average Speed (km/h)"), _("Monthly Average Speed"),"g"
		elif value == 4:
			return 12,_("month"),_("Calories"), _("Monthly Calories"),"b"

	def get_values(self,values,value_selected,monthsnumber):
		#hacemos una relacion entre el value_selected y los values
		conv = {
			0: 1, #value 0 es kilometros (1)
			1: 2, #value 1 es tiempo (2)
			2: 3, #value 2 es pulsaciones(3)
			3: 5, #value 3 es media(5)
			4: 6 #value 4 es calorias(6)
			}
		list_values = {}
		list_average = {}
		tm_total = {}
		for i in range(1,monthsnumber+1):
			list_values[i]=0
			list_average[i]=0
			tm_total[i] = 0
			
		value_sel = conv[value_selected]

		for value in values:
			date = value[0]
			year,month,day = date.split("-")
			month = int(month)
			#si la opcion es tiempo lo pasamos a horas / if the option is time we passed it to hours
			if (value_sel == 2):
				graph_value = self.getFloatValue(value[value_sel])/3600
			else:
				graph_value = self.getFloatValue(value[value_sel])

			#si es una opcion de suma de absolutos / if it is an option of sum of absolute
			if ((value_selected == 0) or (value_selected==1) or (value_selected==4)):
				list_values[int(month)] += graph_value
			#si se trata de calcular medias / if one is to calculate averages:
			else:
				if graph_value is not None and graph_value != 0:
					list_values[int(month)] += graph_value
					list_average[int(month)] += 1

		xunits = []
		yunits = []
		for i in range (0,monthsnumber):
			xunits.append(unicode(calendar.month_abbr[i+1]))
			yunits.append(float(0))
		for value in list_values:
			if ((value_selected == 0) or (value_selected==1) or (value_selected==4)):
				yunits[value-1] = list_values[value]
			else:
				if list_average[value]>0:
					yunits[value-1] = list_values[value]/list_average[value]
		return xunits,yunits
	
	def getFloatValue(self, value):
		try:
			return float(value)
		except:
			return float(0)
