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

import logging
from gui.drawArea import DrawArea

class RecordGraph:
	def __init__(self, vbox = None, window = None, combovalue = None, combovalue2 = None):
		logging.debug(">>")		
		self.drawarea = DrawArea(vbox, window)
		self.combovalue = combovalue
		self.combovalue2 = combovalue2
		logging.debug("<<")

	def drawgraph(self,values):
		logging.debug(">>")
		xval = []
		yval = []
		xlab = []
		ylab = []
		tit = []
		col = []
		value_selected = self.combovalue.get_active()
		logging.debug("Value selected 1: "+ str(value_selected))
		value_selected2 = self.combovalue2.get_active()
		logging.debug("Value selected 2: "+ str(value_selected2))
		if value_selected < 0:
			self.combovalue.set_active(0)
			value_selected = 0
		
		if value_selected2 < 0:
			self.combovalue2.set_active(0)
			value_selected2 = 0

		xvalues, yvalues = self.get_values(values,value_selected)
		xlabel,ylabel,title,color = self.get_value_params(value_selected)

		xval.append(xvalues)
		yval.append(yvalues)
		if value_selected2 > 0:
			xlab.append("")
		else:
			xlab.append(xlabel)
		ylab.append(ylabel)
		tit.append(title)
		col.append(color)
		
		if value_selected2 > 0:
			value_selected2 = value_selected2-1
			xlabel,ylabel,title,color = self.get_value_params(value_selected2)
			xvalues,yvalues = self.get_values(values,value_selected2)
			xval.append(xvalues)
			yval.append(yvalues)
			xlab.append(xlabel)
			ylab.append(ylabel)
			tit.append("")
			col.append(color)		
		logging.info("To show: tit: "+str(tit)+" | col: "+str(col)+" | xlab: "+str(xlab)+" | ylab: "+str(ylab))
		self.drawarea.stadistics("plot",xval,yval,xlab,ylab,tit,col)
		logging.debug("<<")

	def get_value_params(self,value):
		if value == 0:
			return _("Distance (km)"),_("Height (m)"),_("Stage Profile"),"#747400"
		if value == 1:
			return _("Distance (km)"),_("Speed (Km/h)"),_("Speed"),"#007474"
                if value == 2:
                        return _("Distance (km)"),_("Pace (min/km)"),_("Pace"),"#747400"
                if value == 3:
                        return _("Distance (km)"),_("Beats (bpm)"),_("Heart Rate"),"#740074"


	def get_values(self,values, value_selected):
		logging.debug(">>")
		xvalue = []
		yvalue = []
		for value in values:
			xvalue.append(value[0])
			if value_selected==0:
				yvalue.append(value[1])
			if value_selected==1:
				yvalue.append(value[3])
			if value_selected==2:
				try:
                                	yvalue.append(60/value[3])
				except:
                                	yvalue.append(0)
			if value_selected==3:
                                yvalue.append(value[6])
		logging.debug("<<")
		return xvalue,yvalue
	
	def getFloatValue(self, value):
		try:
			return float(value)
		except:
			return float(0)

