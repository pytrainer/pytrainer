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
from .gui.drawArea import DrawArea

from gi.repository import Gtk

class RecordGraph:
    def __init__(self, vbox = None, window = None, combovalue = None, combovalue2 = None, btnShowLaps = None, tableConfig = None, pytrainer_main=None):
        logging.debug(">>")
        self.pytrainer_main = pytrainer_main
        self.drawarea = DrawArea(vbox, window)
        self.combovalue = combovalue
        self.combovalue2 = combovalue2
        self.showLaps = btnShowLaps
        self.config_table = tableConfig
        logging.debug("<<")

    def drawgraph(self,values,laps=None, y1limits=None, y1color=None, y1_linewidth=1):
        logging.debug(">>")
        #Get the config options
        for child in self.config_table.get_children():
            if child.get_name() == "spinbuttonY1Max":
                spinbuttonY1Max = child
            elif child.get_name() == "spinbuttonY1Min":
                spinbuttonY1Min = child
            elif child.get_name() == "colorbuttonY1LineColor":
                colorbuttonY1LineColor = child
            elif child.get_name() == "spinbuttonY1LineWeight":
                spinbuttonY1LineWeight = child

        xval = []
        yval = []
        xlab = []
        ylab = []
        tit = []
        col = []
        value_selected = self.combovalue.get_active()
        logging.debug("Value selected 1: %s", value_selected)
        value_selected2 = self.combovalue2.get_active()
        logging.debug("Value selected 2: %s", value_selected2)
        showLaps = self.showLaps.get_active()
        logging.debug("Show laps: %s", showLaps)
        #Determine left and right lap boundaries
        if laps is not None and showLaps:
            lapValues = []
            lastPoint = 0.0
            for lap in laps:
                thisPoint = float(lap['distance'])/1000.0 + lastPoint
                lapValues.append((lastPoint, thisPoint))
                lastPoint = thisPoint
        else:
            lapValues = None

        if value_selected < 0:
            self.combovalue.set_active(0)
            value_selected = 0

        if value_selected2 < 0:
            self.combovalue2.set_active(0)
            value_selected2 = 0
        xvalues, yvalues = self.get_values(values,value_selected)
        max_yvalue = max(yvalues)
        min_yvalue = min(yvalues)
        xlabel,ylabel,title,color = self.get_value_params(value_selected)
        if y1color is not None:
            _color = Gdk.Color(y1color)
            color = y1color
        else:
            _color = Gdk.Color(color)

        xval.append(xvalues)
        yval.append(yvalues)
        if value_selected2 > 0:
            xlab.append("")
        else:
            xlab.append(xlabel)
        ylab.append(ylabel)
        tit.append(title)
        col.append(color)

        #_color = Gdk.Color(color)
        colorbuttonY1LineColor.set_color(_color)

        if value_selected2 > 0:
            value_selected2 = value_selected2-1
            xlabel,ylabel,title,color = self.get_value_params(value_selected2)
            xvalues,yvalues = self.get_values(values,value_selected2)
            max_yvalue=max(max(yvalues), max_yvalue)
            min_yvalue=min(min(yvalues), min_yvalue)
            xval.append(xvalues)
            yval.append(yvalues)
            xlab.append(xlabel)
            ylab.append(ylabel)
            tit.append("")
            col.append(color)
        logging.info("To show: tit: %s | col: %s | xlab: %s | ylab: %s", tit, col, xlab, ylab)
        #self.drawPlot(xvalues,yvalues,xlabel,ylabel,title,color,zones)
        plot_stats = self.drawarea.drawPlot(xval,yval,xlab,ylab,tit,col,None,lapValues, ylimits=y1limits, y1_linewidth=y1_linewidth)
        ymin = plot_stats['y1_min']
        ymax = plot_stats['y1_max']
        y1_linewidth = plot_stats['y1_linewidth']

        max_yvalue = max(max_yvalue, ymax)
        min_yvalue = min(min_yvalue, ymin)
        adjY1Min = Gtk.Adjustment(value=ymin, lower=min_yvalue,upper=max_yvalue, step_incr=1, page_incr=10)
        adjY1Max = Gtk.Adjustment(value=ymax, lower=min_yvalue,upper=max_yvalue, step_incr=1, page_incr=10)
        spinbuttonY1Min.set_adjustment(adjY1Min)
        spinbuttonY1Max.set_adjustment(adjY1Max)
        spinbuttonY1Min.set_value(ymin)
        spinbuttonY1Max.set_value(ymax)
        spinbuttonY1LineWeight.set_value(y1_linewidth)

        logging.debug("<<")

    def get_value_params(self,value):
        if value == 0:
            return _("Distance (km)"),_("Height (m)"),_("Stage Profile"),"#000000"
        if value == 1:
            return _("Distance (km)"),_("Speed (Km/h)"),_("Speed"),"#00ff00"
        if value == 2:
            return _("Distance (km)"),_("Pace (min/km)"),_("Pace"),"#0000ff"
        if value == 3:
            return _("Distance (km)"),_("Beats (bpm)"),_("Heart Rate"),"#ff0000"
        if value == 4:
            return _("Distance (km)"),_("Cadence (rpm)"),_("Cadence"),"#7B3F00"
        if value == 5:
            return _("Distance (km)"),_("Beats (%)"),_("Beats"),"#ff0000"
        if value == 6:
            return _("Distance (km)"),_("Zone"),_("Zone"),"#ff0000"


    def get_values(self,values, value_selected):
        logging.debug(">>")
        xvalue = []
        yvalue = []
        zones = self.pytrainer_main.profile.getZones()
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
            if value_selected==4:
                yvalue.append(value[7])
            if value_selected==5:
                if value[6] <= zones[4][0]:
                    yvalue.append(50.0*value[6]/zones[4][0])
                else:
                    yvalue.append(50.0+50.0*((value[6]-zones[4][0])/(zones[0][1]-zones[4][0])))
            if value_selected==6:
                if value[6] <= zones[4][0]:
                    yvalue.append(1.0*value[6]/zones[4][0])
                else:
                    yvalue.append(1.0+5.0*((value[6]-zones[4][0])/(zones[0][1]-zones[4][0])))
        logging.debug("<<")
        return xvalue,yvalue

    def getFloatValue(self, value):
        try:
            return float(value)
        except:
            return float(0)

