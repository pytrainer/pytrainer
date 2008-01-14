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

class HeartRateGraph:
	def __init__(self, vbox = None):
		self.drawarea = DrawArea(vbox)

	def drawgraph(self,values):
		value_selected = -1
		if value_selected < 0:
			value_selected = 0
                if value_selected == 0:
                        xvalues, yvalues = self.get_values(values,value_selected)
                        xlabel,ylabel,title,color = self.get_value_params(value_selected)
                        self.drawarea.stadistics("plot",[xvalues],[yvalues],[xlabel],[ylabel],[title],[color])

	def get_value_params(self,value):
                if value == 0:
                        return _("Distance (km)"),_("Beats (bpm)"),_("Heart Rate"),"#740074"


	def get_values(self,values, value_selected):
		xvalue = []
		yvalue = []
		for value in values:
			xvalue.append(value[0])
			if value_selected==0:
                                yvalue.append(value[6])
		return xvalue,yvalue
	
	def getFloatValue(self, value):
		try:
			return float(value)
		except:
			return float(0)

