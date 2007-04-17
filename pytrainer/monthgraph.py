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

class MonthGraph:
	def __init__(self, vbox = None, combovalue = None):
		self.drawarea = DrawArea(vbox)
		self.combovalue = combovalue

	def drawgraph(self,values):
		value_selected = self.combovalue.get_active()
		if value_selected < 0:
			self.combovalue.set_active(0)
			value_selected = 0
		daysmonth,xlabel,ylabel,title,color = self.get_value_params(value_selected)
		xvalues,yvalues = self.get_values(values,value_selected,daysmonth)
		self.drawarea.stadistics("bars",[xvalues],[yvalues],[xlabel],[ylabel],[title],[color])

	def get_value_params(self,value):
		if value == 0:
			return 32,_("day"),_("kilometers"),_("daily kilometers"),"y"
		elif value == 1:
			return 32,_("day"),_("time in hours"), _("daily time"),"b"
		elif value == 2:
			return 32,_("day"),_("beats per minute"), _("daily beats"),"r"
		elif value == 3:
			return 32,_("day"),_("average (hm/h)"), _("daily averages"),"g"
		elif value == 4:
			return 32,_("day"),_("calories"), _("daily calories"),"b"

	def get_values(self,values,value_selected,daysmonth):
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
		for i in range(1,32):
			list_values[i]=0
			list_average[i]=0

		value_sel = conv[value_selected]
		for value in values:
			#si la opcion es tiempo lo pasamos a horas
			if (value_sel == 2):
				graph_value = self.getFloatValue(value[value_sel])/3600
			else:
				graph_value = self.getFloatValue(value[value_sel])
				 
			date = value[0]
			year,month,day = date.split("-")

			#si es una opcion de suma de absolutos:
                        if ((value_selected == 0) or (value_selected==1)):
                                list_values[int(day)] += graph_value
                        #si se trata de calcular medias:
                        else:
                                list_values[int(day)] += graph_value
                                list_average[int(day)] += 1

		xunits = []
		yunits = []
		for i in range (0,daysmonth):
                        xunits.append(i)
			yunits.append(float(0))
		
		for value in list_values:
			yunits[value-1] = list_values[value]	

		return xunits,yunits
	
	def getFloatValue(self, value):
		try:
			return float(value)
		except:
			return float(0)

