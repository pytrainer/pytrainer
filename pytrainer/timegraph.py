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

import datetime
import logging
from pytrainer.gui.drawArea import DrawArea
from pytrainer.lib.localization import locale_str

class TimeGraph(object):
    def __init__(self, sports, vbox = None, window = None, combovalue = None, combovalue2 = None, main = None):
        self.drawarea = DrawArea(vbox, window)
        self.SPORT_FIELD = 9
        self.sport_colors = dict([(sport.name, sport.color.to_hex_string()) for sport in sports])

    def getFloatValue(self, value):
        try:
            return float(value)
        except:
            return float(0)

    def getValue(self,record,value_selected):
        #hacemos una relacion entre el value_selected y los values / we make a relation between value_selected and the values
        conv = {
            0: 'distance', #value 0 es kilometros (1)
            1: 'duration', #value 1 es tiempo (2)
            2: 'beats', #value 2 es pulsaciones(3)
            3: 'average', #value 3 es media(5)
            4: 'calories' #value 4 es calorias(6)
            }
        value_sel = conv[value_selected]
        #si la opcion es tiempo lo pasamos a horas / if the option is time we passed it to hours
        if (value_sel == 'duration'):
            return self.getFloatValue(getattr(record, value_sel))/3600
        else:
            return self.getFloatValue(getattr(record, value_sel))
    
    def get_values(self, values, value_selected, key_format, sportfield=9):
        valueDict = {} #Stores the totals
        valueCount = {} #Counts the totals to allow for averaging if needed
        sportColors = {}

        for record in values:
            if record.date:
                day = locale_str(record.date.strftime(key_format)) # Gives year for this record
                sport = record.sport.name
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
            else:
                logging.debug("No date string found, skipping entry: " + str(record))
                
        if value_selected in (2, 3):
            total = {}
            count = {}
            for sport in valueDict.keys():
                for day in valueDict[sport].keys():
                    if valueCount[sport][day] > 1: #Only average if 2 or more entries on this day
                        valueDict[sport][day] /= valueCount[sport][day]

        if value_selected == 1: #Values are of time type
            valuesAreTime=True
        else:
            valuesAreTime=False

        return valueDict, valuesAreTime

    def drawgraph(self,values, extra=None, x_func=None):
        xval = []
        yval = []
        xlab = []
        ylab = []
        tit = []
        
        valsAreTime = []
        value_selected = self.combovalue.get_active()
        value_selected2 = self.combovalue2.get_active()
        if value_selected < 0:
            self.combovalue.set_active(0)
            value_selected = 0

        y1,ylabel,title,y2 = self.get_value_params(value_selected)
        ylab.append(ylabel)
        tit.append(title)

        yvalues, valuesAreTime = self.get_values(values,value_selected, self.KEY_FORMAT, sportfield=self.SPORT_FIELD)
        xvalues = x_func(yvalues) 
        
        yval.append(yvalues)
        xlab.append(xvalues)
        valsAreTime.append(valuesAreTime)

        #Second combobox used
        if value_selected2 > 0:
            value_selected2 = value_selected2-1
            y1, ylabel,title,y2 = self.get_value_params(value_selected2)
            ylab.append(ylabel)
            tit.append(title)
            yvalues, valuesAreTime = self.get_values(values,value_selected2, self.KEY_FORMAT, sportfield=self.SPORT_FIELD)
            yval.append(yvalues)
            xlab.append(xvalues)
            valsAreTime.append(valuesAreTime)
        #Draw chart
        self.drawarea.drawStackedBars(xlab,yval,ylab,tit,valsAreTime, colors = self.sport_colors)

    def get_value_params(self,value):
        return self.value_params[value]

