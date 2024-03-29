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

import matplotlib
matplotlib.use('GTK3Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvasGTK
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar
import matplotlib.pyplot as plt
import pylab
import logging

class DrawArea:
    def __init__(self, vbox = None, window = None):
        logging.debug('>>')
        #self.figure = Figure(figsize=(6,4), dpi=72)
        #self.axis = self.figure.add_subplot(111)
        self.vbox = vbox
        self.window = window
        #self.canvas = FigureCanvasGTK(self.figure) # a gtk.DrawingArea
        #self.drawDefault()
        self.NEARLY_ZERO = 0.0000000000000000000001
        logging.debug('<<')

    def statistics(self,type,xvalues,yvalues,xlabel,ylabel,title,color=None,zones=None):
        logging.debug('>>')
        if len(xvalues[0]) < 1:
            #self.drawDefault()
            return False
        #logging.debug('xvalues: '+str(xvalues))
        #logging.debug('yvalues: '+str(yvalues))
        #logging.debug("Type: "+type+" | title: "+str(title)+" | col: "+str(color)+" | xlabel: "+str(xlabel)+" | ylabel: "+str(ylabel))
        if type == "plot":
            self.drawPlot(xvalues,yvalues,xlabel,ylabel,title,color,zones)
        elif type == "pie" or type == "histogram":
            self.drawZones(type,xvalues,yvalues,xlabel,ylabel,title,color,zones)
        logging.debug('<<')

    def getColor(self, x):
        colors=["b","g","r","c","m","y","k", "w"]
        if x >= len(colors):
            x = x % len(colors)
        return colors[x]

    def fmtTableText(self, x, valuesAreTime):
        if x <= 0.0001:
            return ' '
        elif valuesAreTime:
            hour = int(x)
            minutes = int((x-hour)*60)
            hourLabel = _("h")
            minLabel = _("min")
            if hour > 0:
                return "%d%s %02d%s" % (hour, hourLabel, minutes, minLabel)
            else:
                return "%02d%s" % (minutes, minLabel)
        else:
            return '%1.1f' % x

    def drawStackedBars(self,xvalues,yvalues,ylabel,title, valuesAreTime=False, colors={}):
        '''function to draw stacked bars
            xvalues needs to be a list of lists of strings, e.g. [0]["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            yvalues needs to be a list of dicts e.g. [0]{'Kayak': {'Tue': 10.08, 'Fri': 17.579999999999998, 'Thu': 15.66, 'Sat': 30.619999999999997}, {'Run': {'Mon': 9.65, 'Sun': 15.59}}
        '''
        #TODO tidy
        logging.debug('>>')
        logging.debug("Title: %s", title)
        logging.debug("X values received: %s", xvalues)
        logging.debug("Y values received: %s", yvalues)
        self.removeVboxChildren()

        #Check how many axes to draw
        if len(xvalues) == 1: #One axis
            barWidth = 0.8
            barOffset = 0.1
        elif len(xvalues) == 2: #Twin axes
            barWidth = 0.4
            barOffset = 0.1
        else: #Error
            return

        keys = list(yvalues[0].keys()) # days of the week
        numRows = len(keys)
        numCols = len(xvalues[0])
        if numRows == 0:
            return
        width = .8
        #figure = plt.figure(figsize=(6,4), dpi=72)
        figure = plt.figure()
        logging.debug("Figure: %s", figure)
        axis = plt.subplot(111)

        ybottoms = [0] * numCols
        yheights = [0] * numCols
        inds = range(0, numCols)
        xvals = [x+barOffset for x in range(0, numCols)]
        cellText = []
        self.showGraph=False

        for k in colors:
            if colors[k]==None: colors[k]=''

        #Display first axis
        xticks = []
        for key in keys:
            logging.debug("Day of the week: %s", key)
            for ind in inds:
                ybottoms[ind] += yheights[ind]
                yheights[ind] = 0 #Zero heights
            color = "#"+colors.get(key, '')
            if len(color)<2:
                color = self.getColor(keys.index(key))
            for xvalue in xvalues[0]:
                index = xvalues[0].index(xvalue)
                if xvalue in yvalues[0][key]:
                    height = yvalues[0][key][xvalue]
                    if float(height) > 0.0:
                        self.showGraph=True
                else:
                    height = self.NEARLY_ZERO
                yheights[index] = height
            cellText.append([self.fmtTableText(x, valuesAreTime[0]) for x in yheights])
            if self.showGraph:
                axis.bar(xvals, yheights, bottom=ybottoms, width=barWidth, color=color,  align='edge', label=key)
            else:   #Only zero results
                pass
        axis.set_xticklabels('' * len(xvalues[0]))
        axis.set_ylabel(ylabel[0])
        if len(xvalues) == 1:
            plt.title(title[0])
            axis.legend(loc=0)

        axis.set_xlim(0,numCols)

        logging.debug("X values first axis: %s", xvals)
        logging.debug("Y values first axis: %s", yheights)

        #Display twin axis
        if len(xvalues) == 2:
            self.showGraph=False
            ax2 = axis.twinx()
            keys = list(yvalues[1].keys())
            ybottoms = [0] * numCols
            yheights = [self.NEARLY_ZERO] * numCols
            for key in keys:
                for ind in inds:
                    ybottoms[ind] += yheights[ind]
                    yheights[ind] = 0.0 #Zero heights
                color = "#"+colors.get(key, '')
                if len(color)<2:
                    color = self.getColor(keys.index(key))
                for xvalue in xvalues[0]:
                    index = xvalues[0].index(xvalue)
                    if xvalue in yvalues[1][key]:
                        height = yvalues[1][key][xvalue]
                        if float(height) > 0.0:
                            self.showGraph=True
                    else:
                        height = self.NEARLY_ZERO
                    yheights[index] = height
                    textToAdd = self.fmtTableText(height, valuesAreTime[1])
                    if textToAdd != ' ':
                        row = keys.index(key)
                        col = index
                        cellText[row][col] += " | %s" % (self.fmtTableText(height, valuesAreTime[1]))
                        #print "Would add %s to %s %s" % (self.fmtTableText(height, valuesAreTime[1]), index, keys.index(key))
                if self.showGraph:
                    xvals = [x+barOffset+barWidth for x in range(0, numCols)]
                    #print "ax2", xvals, yheights, ybottoms
                    ax2.bar(xvals, yheights, bottom=ybottoms, width=barWidth, color=color,  align='edge', label=key)
                else:   #Only zero results
                    ax2.bar(xvals, [0]*numCols, bottom=[0]*numCols, width=barWidth, color=color,  align='edge', label=key)
                    pass
            ax2.set_xticklabels('' * len(xvalues[1]))
            ax2.set_xlim(0,numCols)
            ax2.set_ylabel(ylabel[1])
            ax2.legend(loc=0)
            plt.title("%s vs %s" %(title[0],title[1]))

        ## try to do some table stuff
        colLabels = xvalues[0]
        rowLabels = keys
        axis.table(cellText=cellText, cellLoc='center', rowLabels=rowLabels, colLabels=colLabels, loc='bottom')
        plt.subplots_adjust(left=0.15,bottom=0.08+(0.03*numRows))
        axis.grid(True)
        canvas = FigureCanvasGTK(figure) # a gtk.DrawingArea
        canvas.show()
        self.vbox.pack_start(canvas, True, True, 0)

        for child in self.vbox.get_children():
            logging.debug('Child available: %s', child)

        logging.debug('<<')

    def drawPlot(self,xvalues,yvalues,xlabel,ylabel,title,color,zones=None,xzones=None, ylimits=None, y1_linewidth=None):
        logging.debug('>>')
        logging.debug("Type: plot | title: %s | col: %s | xlabel: %s | ylabel: %s",
                      title, color, xlabel, ylabel)
        logging.debug('xlabel: %s | ylabel: %s | title: %s', xlabel, ylabel, title)
        self.removeVboxChildren()
        figure = plt.Figure()
        logging.debug("Figure: %s", figure)
        #figure.clf()
        i = 0
        for value in xvalues:
            if i<1:
                logging.debug("i: %d, value: (%s) %s %s", i, value, xvalues, yvalues)
                axis = figure.add_subplot(111)
                logging.debug("Axis: %s", axis)
                line = axis.plot(xvalues[i],yvalues[i], color=color[i])
                logging.debug("Axis plotted, Line: %s", line)
                if y1_linewidth is not None:
                    line[0].set_linewidth(y1_linewidth)
                linewidth = line[0].get_linewidth()

                axis.grid(True)
                logging.debug("Axis grid on" )
                for tl in axis.get_yticklabels():
                    tl.set_color('%s' %color[i])
                logging.debug("Ticklabels color set" )
                #Draw zones on graph, eg for each lap
                if xzones is not None:
                    logging.debug("Setting xzones" )
                    for xzone in xzones:
                        if xzones.index(xzone) % 2:
                            zonecolor='b'
                        else:
                            zonecolor='g'
                        axis.axvspan(xzone[0], xzone[1], alpha=0.25, facecolor=zonecolor)
                maxX = max(xvalues[i])
            if i>=1:
                ax2 = axis.twinx()
                logging.debug("Axis2: Axis: %s", ax2)
                ax2.plot(xvalues[i], yvalues[i], color=color[i])
                logging.debug("Axis2: plotted" )
                for tl in ax2.get_yticklabels():
                    tl.set_color('%s' %color[i])
                logging.debug("Axis2: Ticklabels color set" )
                maxXt = max(xvalues[i])
                if maxXt > maxX:
                    maxX = maxXt
            axis.set_xlabel(xlabel[i])
            logging.debug("X label set" )
            i+=1
        axis.set_xlim(0, maxX)

        if (len(xvalues)>1):
            axis.set_title("%s vs %s" %(ylabel[0],ylabel[1]))
        else:
            axis.set_title("%s" %(ylabel[0]))

        ylim_min, ylim_max = axis.get_ylim()
        if ylimits is not None:
            logging.debug("Using ylimits: %s", ylimits)
            if ylimits[0] is not None:
                ylim_min = ylimits[0]
            if ylimits[1] is not None:
                ylim_max = ylimits[1]
            axis.set_ylim(ylim_min, ylim_max)

        canvas = FigureCanvasGTK(figure) # a gtk.DrawingArea
        logging.debug("Canvas: %s", canvas)
        canvas.show()
        self.vbox.pack_start(canvas, True, True, 0)
        toolbar = NavigationToolbar(canvas)
        self.vbox.pack_start(toolbar, False, False, 0)

        for child in self.vbox.get_children():
            logging.debug('Child available: %s', child)

        logging.debug('<<')
        return {'y1_min': ylim_min, 'y1_max': ylim_max, 'y1_linewidth': linewidth}

    def drawZones(self,shape,xvalues,yvalues,xlabel,ylabel,title,color,zones=None):
        logging.debug('>>')
        logging.debug("Type: %s | title: %s | col: %s | xlabel: %s | ylabel: %s",
                      shape, title, color, xlabel, ylabel)
        self.removeVboxChildren()
        figure = Figure()
        logging.debug("Figure: %s", figure)
        axis = figure.add_subplot(111)

        labels = [_("rest")]
        colors = ["#ffffff"]
        for zone in reversed(zones):
            labels.append(zone[3])
            colors.append(zone[2])

        zone_sum = [0]*6
        for value in yvalues[0]:
            # bisection, it's faster
            if not value:
                zone_sum[0] += 1
            elif value <= zones[2][1]:
                if value <= zones[4][1]:
                    if value <= zones[4][0]:
                        zone_sum[0] += 1
                    else:
                        zone_sum[1] += 1
                else:
                    if value <= zones[3][1]:
                        zone_sum[2] += 1
                    else:
                        zone_sum[3] += 1
            else:
                if value <= zones[1][1]:
                    zone_sum[4] += 1
                else:
                    zone_sum[5] += 1

        if shape == "pie":
            self._piePlot(axis, zone_sum, colors, labels)
        elif shape == "histogram":
            self._barPlot(axis, zone_sum, colors, labels)

        canvas = FigureCanvasGTK(figure) # a gtk.DrawingArea
        canvas.show()

        for child in self.vbox.get_children():
            logging.debug('Child available: %s', child)

        self.vbox.pack_start(canvas, True, True, 0)
        logging.debug('<<')

    def _barPlot(self, axis, zone_sum, colors, labels):
        invtotal = 100.0/sum(zone_sum)
        fracs = [i*invtotal for i in zone_sum]
        xticks = list(range(len(fracs)))

        axis.bar(xticks, fracs, color=colors, align="center")
        axis.set_xticks(xticks)
        axis.set_xticklabels(labels)
        axis.set_ylabel(_("Time in zone [%]"))

    def _piePlot(self, axis, zone_sum, colors, labels):
        labels_trunc = [l for z,l in zip(zone_sum, labels) if z > 0]
        colors_trunc = [c for z,c in zip(zone_sum, colors) if z > 0]
        zone_trunc   = [z for z in zone_sum if z > 0]
        explode      = [0]*len(zone_trunc)
        axis.pie(zone_trunc, explode=explode, labels=labels_trunc, colors=colors_trunc, autopct='%1.1f%%', shadow=True)

    def drawDefault(self):
        logging.debug('>>')
        self.axis=self.figure.add_subplot(111)
        self.axis.set_xlabel('Yepper')
        self.axis.set_ylabel('Flabber')
        self.axis.set_title('An Empty Graph')
        self.axis.grid(True)
        self.canvas.destroy()
        self.canvas = FigureCanvasGTK(self.figure) # a gtk.DrawingArea
        self.canvas.show()
        self.vbox.pack_start(self.canvas, True, True, 0)
        logging.debug('<<')

    def fill_over(self, ax, x, y, val, color, over=True):
        """
        Plot filled x,y for all y over val
        if over = False, fill all areas < val
        """
        logging.debug('>>')
        ybase = asarray(y)-val
        crossings = nonzero(less(ybase[:-1] * ybase[1:],0))

        if ybase[0]>=0:
            fillon = over
        else:
            fillon = not over
        indLast = 0
        for ind in crossings:
            if fillon:
                thisX = x[indLast:ind+1]
                thisY = y[indLast:ind+1]
                thisY[0] = val
                thisY[-1] = val
                ax.fill(thisX, thisY, color)
            fillon = not fillon
            indLast = ind
        logging.debug('<<')

    def removeVboxChildren(self):
        ''' function to delete vbox children so that multiple graphs do not appear
            there must a better way to do this - pyplot?
        '''
        logging.debug('>>')
        #Tidy up draw areas
        vboxChildren = self.vbox.get_children()
        logging.debug('Vbox has %d children %s', len(vboxChildren), vboxChildren)
        # ToDo: check why vertical container is shared
        for child in vboxChildren:
            #Remove all FigureCanvasGTK and NavigationToolbar2GTKAgg to stop double ups of graphs
            if isinstance(child, FigureCanvasGTK) or isinstance(child, NavigationToolbar):
                logging.debug('Removing child: %s', child)
                self.vbox.remove(child)
        logging.debug('<<')
