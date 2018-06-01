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

import dateutil
import datetime
from .timegraph import TimeGraph

class MonthGraph(TimeGraph):

    value_params = [
        (_("day"),_("Distance (km)"),_("Daily Distance"),"y"),
        (_("day"),_("Time (hours)"), _("Daily Time"),"b"),
        (_("day"),_("Average Heart Rate (bpm)"), _("Daily Average Heart Rate"),"r"),
        (_("day"),_("Average Speed (km/h)"), _("Daily Average Speed"),"g"),
        (_("day"),_("Calories"), _("Daily Calories"),"b"),
    ]

    def __init__(self, sports, vbox = None, window = None, combovalue = None, combovalue2 = None, main = None):
        TimeGraph.__init__(self, sports, vbox=vbox, window=window, main=main)
        self.combovalue = combovalue
        self.combovalue2 = combovalue2
        self.KEY_FORMAT = "%d"
        
    def drawgraph(self,values, daysInMonth):
        TimeGraph.drawgraph(self, values, x_func=lambda x: list([u'%02d' % d for d in range(1,daysInMonth+1)]))

    def get_values2(self,values,value_selected,daysInMonth):
        #hacemos una relacion entre el value_selected y los values / we make a relation between value_selected and the values
        conv = {
            0: 1, #value 0 es kilometros (1)
            1: 2, #value 1 es tiempo (2)
            2: 3, #value 2 es pulsaciones(3)
            3: 5, #value 3 es media(5)
            4: 6 #value 4 es calorias(6)
            }
        list_values = {}
        list_average = {}
        for i in range(1,daysInMonth+1):
            list_values[i]=0
            list_average[i]=0

        value_sel = conv[value_selected]
        for value in values:
            #si la opcion es tiempo lo pasamos a horas / if the option is time we passed it to hours
            if (value_sel == 2):
                graph_value = self.getFloatValue(value[value_sel])/3600
            else:
                graph_value = self.getFloatValue(value[value_sel])
                 
            #TODO Sort date handling...
            date = value[0]
            try:
                year,month,day = date.year, date.month, date.day
            except AttributeError:
                year,month,day = date.split("-")

            #si es una opcion de suma de absolutos / if it is an option of sum of absolute
            if ((value_selected == 0) or (value_selected==1) or (value_selected==4)):
                list_values[int(day)] += graph_value
            #si se trata de calcular medias / if one is to calculate averages:
            else:
                if graph_value is not None and graph_value != 0:
                    list_values[int(day)] += graph_value
                    list_average[int(day)] += 1

        xunits = []
        yunits = []
        for i in range (1,daysInMonth+1):
            xunits.append(i)
            yunits.append(float(0))
    
        for value in list_values:
            if ((value_selected == 0) or (value_selected==1) or (value_selected==4)):
                yunits[value-1] = list_values[value]
            else:
                if list_average[value]>0:
                    yunits[value-1] = list_values[value]/list_average[value]

        return xunits,yunits
    
