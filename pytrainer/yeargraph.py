# -*- coding: utf-8 -*-

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

from pytrainer.timegraph import TimeGraph

class YearGraph(TimeGraph):

    value_params = [
        (_("month"),_("Distance (km)"),_("Monthly Distance"),"y"),
        (_("month"),_("Time (hours)"), _("Monthly Time"),"b"),
        (_("month"),_("Average Heart Rate (bpm)"), _("Monthly Average Heart Rate"),"r"),
        (_("month"),_("Average Speed (km/h)"), _("Monthly Average Speed"),"g"),
        (_("month"),_("Calories"), _("Monthly Calories"),"b"),
    ]

    def __init__(self, sports, vbox = None, window = None, combovalue = None, combovalue2 = None, main = None):
        TimeGraph.__init__(self, sports, vbox=vbox, window=window, main=main)
        self.combovalue = combovalue
        self.combovalue2 = combovalue2
        self.KEY_FORMAT = "%m"

    def drawgraph(self,values):
        TimeGraph.drawgraph(self, values, x_func=lambda x: ["%02d" % m for m in range(1,13)])
