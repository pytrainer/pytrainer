# -*- coding: iso-8859-1 -*-

#Copyright (C) Sigurður H. Pálsson shp@itn.is

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

from timegraph import TimeGraph

class TotalGraph(TimeGraph):

    value_params = [
        (_("year"),_("Distance (km)"),_("Annual Distance"),"y"),
        (_("year"),_("Time (hours)"), _("Annual Time"),"b"),
        (_("year"),_("Average Heart Rate (bpm)"), _("Annual Average Heart Rate"),"r"),
        (_("year"),_("Average Speed (km/h)"), _("Annual Average Speed"),"g"),
        (_("year"),_("Calories"), _("Annual Calories"),"b"),
    ]

    def __init__(self, vbox = None, window = None, combovalue = None, combovalue2 = None):
        TimeGraph.__init__(self, vbox=vbox, window=window)
        self.combovalue = combovalue
        self.combovalue2 = combovalue2
        self.KEY_FORMAT = "%Y"
        self.SPORT_FIELD = 4

    def getYears(self, yvalues):
        years = set()
        for s in yvalues.values():
            years |= set([str(x) for x in xrange(int(min(s.keys())), int(max(s.keys()))+1)])
        return sorted(list(years))

    def drawgraph(self,values):
        TimeGraph.drawgraph(self, values, x_func=self.getYears)

    def getValue(self,record,value_selected):
        #hacemos una relacion entre el value_selected y los values / we make a relation between value_selected and the values
        conv = {
            0: 1, #value 0 es kilometros (1)
            1: 6, #value 1 es tiempo (2)
            2: 7, #value 2 es pulsaciones(3)
            3: 5, #value 3 es media(5)
            4: 8 #value 4 es calorias(6)
            }
        value_sel = conv[value_selected]
        #si la opcion es tiempo lo pasamos a horas / if the option is time we passed it to hours
        if (value_sel == 6):
            return self.getFloatValue(record[value_sel])/3600
        else:
            return self.getFloatValue(record[value_sel])
    

