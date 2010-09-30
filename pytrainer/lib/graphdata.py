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
import gtk

class GraphData:
    '''
    Class to hold data and formating for graphing via matplotlib
    '''
    def __init__(self, title=None, ylabel=None, xlabel=None):
        logging.debug('>>')
        self.title = title
        self.ylabel = ylabel
        self.xlabel = xlabel
        self.x_values = []
        self.bar_bottoms = []
        self.bar_widths = []
        self.y_values = []
        self.linewidth = 1
        self.linecolor = '#ff0000'
        self.max_x_value = None
        self.min_x_value = None
        self.max_y_value = None
        self.min_y_value = None
        self.graphType = "plot"
        self.show_on_y1 = False
        logging.debug('<<')
        
    def addBars(self, x=None, y=None):
        if x is None or y is None:
            #logging.debug("Must supply both x and y data points, got x:'%s' y:'%s'" % (str(x), str(y)))
            return
        #print('Adding point: %s %s' % (str(x), str(y)))
        if len(self.x_values) == 0:
            #First bar, so start a 0
            self.x_values.append(0)
        else:
            #Second or subsequent bar, so start at last point
            #Which is previous left+width
            items = len(self.x_values)
            last_left = self.x_values[items-1]
            last_width = self.bar_widths[items-1]
            new_left = last_left+last_width
            print new_left
            self.x_values.append(new_left)
        self.bar_widths.append(x)            
        self.y_values.append(y)
        self.bar_bottoms.append(0)
        
    def addPoints(self, x=None, y=None):
        if x is None or y is None:
            #logging.debug("Must supply both x and y data points, got x:'%s' y:'%s'" % (str(x), str(y)))
            return
        #print('Adding point: %s %s' % (str(x), str(y)))
        self.x_values.append(x)
        self.y_values.append(y)
        if self.max_x_value is None or x > self.max_x_value:
            self.max_x_value = x
        if self.min_x_value is None or x < self.min_x_value:
            self.min_x_value = x
        if self.max_y_value is None or y > self.max_y_value:
            self.max_y_value = y
        if self.min_y_value is None or y < self.min_y_value:
            self.min_y_value = y

    def set_color(self, color):
        ''' 
            Helper function to set the line color
            need as some gtk.gdk color can be invalid for matplotlib
        '''
        try:
            #Generate 13 digit color string from supplied color
            col = gtk.gdk.color_parse(color).to_string()
        except ValueError:
            logging.debug("Unable to parse color from '%s'" % color)
            return
        #Create matplotlib color string
        _color = "#%s%s%s" % (col[1:3], col[5:7], col[9:11])
        logging.debug("%s color saved as: %s" % (color, _color))
        self.linecolor = _color

    def __len__(self):
        if self.x_values is None:
            return None
        return len(self.x_values)
        
    def __str__(self):
        return '''
Title: %s
ylabel: %s
xlabel: %s
linewidth: %d
linecolor: %s
graphType: %s
show on y1: %s
x min max: %s %s
y min max: %s %s
x values: %s
y values: %s''' % (self.title,
    self.ylabel,
    self.xlabel,
    self.linewidth,
    self.linecolor,
    self.graphType,
    str(self.show_on_y1),
    str(self.min_x_value), str(self.max_x_value),
    str(self.min_y_value), str(self.max_y_value),
    str(self.x_values),
    str(self.y_values)
    )

    



