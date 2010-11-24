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

import matplotlib
#matplotlib.use('GTK')
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvasGTK
#from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
import matplotlib.pyplot as plt
#import pylab
import logging

class DrawGraph:
    def __init__(self, parent = None, pytrainer_main = None):
        logging.debug('>>')
        self.parent = parent
        self.pytrainer_main = pytrainer_main
        #self.NEARLY_ZERO = 0.0000000000000000000001
        self.ax1 = None
        self.ax2 = None
        logging.debug('<<')

    def draw(self, datalist=None, box=None, figure=None, title=None, y2=False, xgrid=False, ygrid=False):
        '''
            Draw a graph using supplied information into supplied gtk.box

            datalist = populated graphdata class (required)
            box = gtk.box object (required)
            figure = matplotlib figure (optional) if supplied will add graph to this figure
            title =
            y2 =

            return = figure
        '''
        logging.debug('>>')
        if box is None:
            logging.error("Must supply a vbox or hbox to display the graph")
            return
        #Check if have a graph object
        if figure is None:
            #No figure, so create figure
            figure = plt.figure()
            self.ax1 = plt.axes()
            #Reset second axis
            self.ax2 = None
        #Remove any existing plots
        for child in box.get_children():
            logging.debug('Removing box child: '+str(child))
            box.remove(child)

        if datalist is None:
            logging.debug("drawPlot called with no data")
            return figure

        if y2 and self.ax2 is None:
            self.ax2 = plt.twinx()


        #Create canvas
        canvas = FigureCanvasGTK(figure) # a gtk.DrawingArea
        canvas.show()

        #Display title etc
        if datalist.xlabel is not None:
            plt.xlabel(datalist.xlabel)
        if title is not None:
            plt.title(title)
        #Display grid
        if y2 and ygrid:
            self.ax2.grid(True)
        elif self.ax1 and ygrid:
            self.ax1.grid(True)
        plt.gca().xaxis.grid(xgrid)
        #Removed as now in legend
        #plt.ylabel(datalist.ylabel)

        #Determine graph type....
        #print "Got graphtype: %s" % datalist.graphType
        #print datalist.x_values
        #print datalist.y_values
        #print datalist.linewidth
        #print datalist.linecolor
        #print datalist.ylabel
        if datalist.graphType == "plot":
            #Plot data
            if not y2:
                #plt.plot(datalist.x_values, datalist.y_values, linewidth=datalist.linewidth, color=datalist.linecolor, label=datalist.ylabel )
                self.ax1.plot(datalist.x_values, datalist.y_values, linewidth=datalist.linewidth, color=datalist.linecolor, label=datalist.ylabel )
            else:
                self.ax2.plot(datalist.x_values, datalist.y_values, linewidth=datalist.linewidth, color=datalist.y2linecolor, label=datalist.ylabel )
        elif datalist.graphType == "bar":
            if not y2:
                self.ax1.bar(datalist.x_values, datalist.y_values, datalist.bar_widths, datalist.bar_bottoms, color=datalist.linecolor, label=datalist.ylabel, alpha=0.5)
            else:
                self.ax2.bar(datalist.x_values, datalist.y_values, datalist.bar_widths, datalist.bar_bottoms, color=datalist.y2linecolor, label=datalist.ylabel, alpha=0.5)
        elif datalist.graphType == "vspan":
            i = 0
            while i < len(datalist.x_values):
                #print datalist.x_values[i] , datalist.bar_widths[i]
                if not y2:
                    self.ax1.axvspan(datalist.x_values[i], datalist.x_values[i]+datalist.bar_widths[i], alpha=0.15, facecolor=datalist.linecolor)
                else:
                    self.ax2.axvspan(datalist.x_values[i], datalist.x_values[i]+datalist.bar_widths[i], alpha=0.15, facecolor=datalist.y2linecolor)
                i += 1
        elif datalist.graphType == "hspan":
            i = 0
            while i < len(datalist.x_values):
                #print datalist.x_values[i] , datalist.y_values[i], datalist.labels[i], datalist.colors[i]
                if not y2:
                    self.ax1.axhspan(datalist.x_values[i], datalist.y_values[i], alpha=0.25, facecolor=datalist.colors[i], label=datalist.labels[i])
                else:
                    self.ax2.axhspan(datalist.x_values[i], datalist.y_values[i], alpha=0.25, facecolor=datalist.colors[i], label=datalist.labels[i])
                i += 1
        elif datalist.graphType == "date":
            if not y2:
                self.ax1.plot_date(datalist.x_values, datalist.y_values, color=datalist.linecolor, label=datalist.ylabel, alpha=0.5)
            else:
                self.ax2.plot_date(datalist.x_values, datalist.y_values, color=datalist.y2linecolor, label=datalist.ylabel, alpha=0.5)
        else:
            print "Unknown/unimplemented graph type: %s" % datalist.graphType
            return figure
        #Set axis limits
        #plt.axis([datalist.min_x_value, datalist.max_x_value, datalist.min_y_value, datalist.max_y_value])
        if self.ax1 is not None:
            self.ax1.legend(loc = 'upper left', bbox_to_anchor = (0, 1))
        if self.ax2 is not None:
            self.ax2.legend(loc = 'upper right', bbox_to_anchor = (1, 1))
        #axis.set_xlim(0, data.max_x_value)
        #axis.set_ylim(0, data.max_y_value)

        #Display plot
        box.pack_start(canvas, True, True)

        logging.debug("<<")
        return figure

    def drawAthleteGraph(self, athlete = None, box = None):
        '''
            Draw a plot style graph
        '''
        logging.debug('>>')
        #TODO - supply athlete class (and have that populated with all data required...
        if box is None:
            logging.error("Must supply a vbox or hbox to display the graph")
            return
        if athlete is None: # or len(datalist) == 0:
            logging.error("Must supply data to graph graph")
            return
        figure = None
        #Debug info - to remove
        #print("drawPlot....")
        for item in athlete.graphdata:
            #print "drawing", item
            #print athlete.graphdata[item]
            figure = self.draw(athlete.graphdata[item], box=box, figure=figure, title=_("Athlete Data"), y2=athlete.graphdata[item].show_on_y2)

    def drawActivityGraph(self, activity = None, box = None):
        '''
            Draw a multiple style graph using data in an activity (with multiple traces on each axis)
        '''
        logging.debug('>>')
        if box is None:
            logging.error("Must supply a vbox or hbox to display the graph")
            return
        if activity is None:
            logging.error("Must supply data to graph graph")
            return
        #TODO Check that datalist is of type dict (and contains has correct items)
        figure = None
        datalist = []
        y1count = 0
        y2count = 0

        if activity.x_axis == "distance":
            if activity.title is None or activity.title == "":
                _title = "%s%s of %s on %s" % (str(activity.distance), activity.distance_unit, activity.sport_name, activity.date)
            else:
                _title = "%s: %s%s of %s on %s" % (activity.title, str(activity.distance), activity.distance_unit, activity.sport_name, activity.date)

            #Loop through data items and graph the selected ones
            for item in activity.distance_data:
                if activity.distance_data[item].show_on_y1:
                    y1count += 1
                    figure = self.draw(activity.distance_data[item], box=box, figure=figure, title=_title, xgrid=activity.x_grid, ygrid=activity.y1_grid)
                if activity.distance_data[item].show_on_y2:
                    y2count += 1
                    figure = self.draw(activity.distance_data[item], box=box, figure=figure, title=_title, y2=True, xgrid=activity.x_grid, ygrid=activity.y2_grid)
            #Display lap divisions if required
            if activity.show_laps:
                figure = self.draw(activity.lap_distance, box=box, figure=figure)

        elif activity.x_axis == "time":
            _time = "%d:%02d:%02d" % (activity.time_tuple)
            if activity.title is None or activity.title == "":
                _title = "%s of %s on %s" % (_time, activity.sport_name, activity.date)
            else:
                _title = "%s: %s of %s on %s" % (activity.title, _time, activity.sport_name, activity.date)
            for item in activity.time_data:
                if activity.time_data[item].show_on_y1:
                    y1count += 1
                    figure = self.draw(activity.time_data[item], box=box, figure=figure, title=_title, xgrid=activity.x_grid, ygrid=activity.y1_grid)
                if activity.time_data[item].show_on_y2:
                    y2count += 1
                    figure = self.draw(activity.time_data[item], box=box, figure=figure, title=_title, y2=True, xgrid=activity.x_grid, ygrid=activity.y2_grid)
            #Display lap divisions if required
            if activity.show_laps:
                figure = self.draw(activity.lap_time, box=box, figure=figure)

        #Sort out graph errors...
        if y1count == 0 and y2count == 0:
            logging.debug("No items to graph.. Removing graph")
            figure = self.draw(None, box=box, figure=figure)
        elif y1count == 0:
            logging.debug("No items on y1 axis... ")
            #TODO Sort
        #Get axis limits..
        if self.ax1 is not None:
            activity.x_limits = self.ax1.get_xlim()
            activity.y1_limits = self.ax1.get_ylim()
        else:
            activity.y1_limits = (None, None)
        if self.ax2 is not None:
            activity.x_limits = self.ax2.get_xlim()
            activity.y2_limits = self.ax2.get_ylim()
        else:
            activity.y2_limits = (None, None)
        #Set axis limits if requested
        #X Axis
        if activity.x_limits_u[0] is not None:
            if self.ax1 is not None:
                self.ax1.set_xlim(activity.x_limits_u)
            elif self.ax2 is not None:
                self.ax2.set_xlim(activity.x_limits_u)
        #Y1 Axis
        if activity.y1_limits_u[0] is not None:
            if self.ax1 is not None:
                self.ax1.set_ylim(activity.y1_limits_u)
        #Y2 Axis
        if activity.y2_limits_u[0] is not None:
            if self.ax2 is not None:
                self.ax2.set_ylim(activity.y2_limits_u)

        return activity
        logging.debug('<<')
