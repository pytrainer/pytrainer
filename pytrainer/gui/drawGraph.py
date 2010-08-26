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
		logging.debug('<<')

	def drawPlot(self, datalist = None, box = None):
		'''
			Draw a plot style graph
		'''
		#data = {'linewidth':3, 'x':(1,2,3), 'y':(3,9,1)}
		logging.debug('>>')
		if box is None:
			logging.error("Must supply a vbox or hbox to display the graph")
			return
		#Remove existing plot (if any)
		for child in box.get_children():
			logging.debug('Removing box child: '+str(child))
			box.remove(child)
		if datalist is None: # or len(datalist) == 0:
			logging.debug("drawPlot called with no data")
			return
		#Debug info - to remove
		print("drawPlot....")
		#print datalist
		
		#Set up drawing area
		figure = plt.figure()
		canvas = FigureCanvasGTK(figure) # a gtk.DrawingArea
		canvas.show()
		#Display title etc
		plt.xlabel(datalist.xlabel)
		plt.ylabel(datalist.ylabel)
		plt.title(datalist.title)
		#Plot data
		plt.plot(datalist.x_values, datalist.y_values, linewidth=datalist.linewidth, color=datalist.linecolor )
		#Set axis limits
		plt.axis([datalist.min_x_value, datalist.max_x_value, datalist.min_y_value, datalist.max_y_value])

		#axis.set_xlim(0, data.max_x_value)
		#axis.set_ylim(0, data.max_y_value)

		#Display plot
		box.pack_start(canvas, True, True)

		return
		#(self,xvalues,yvalues,xlabel,ylabel,title,color,zones=None,xzones=None, ylimits=None, y1_linewidth=None):
		logging.debug("Type: plot | title: "+str(title)+" | col: "+str(color)+" | xlabel: "+str(xlabel)+" | ylabel: "+str(ylabel))
		logging.debug('xlabel: '+str(xlabel)+' | ylabel: '+str(ylabel)+' | title: '+str(title))
		#self.removeVboxChildren()
		i = 0
		for value in xvalues:
			if i<1:
				axis = figure.add_subplot(111)
				line = axis.plot(xvalues[i],yvalues[i], color=color[i])
				if y1_linewidth is not None:
					line[0].set_linewidth(y1_linewidth)
				linewidth = line[0].get_linewidth()

				axis.grid(True)
				for tl in axis.get_yticklabels():
					tl.set_color('%s' %color[i])
				#Draw zones on graph, eg for each lap
				if xzones is not None:
					for xzone in xzones:
						if xzones.index(xzone) % 2:
							zonecolor='b'
						else:
							zonecolor='g'
						axis.axvspan(xzone[0], xzone[1], alpha=0.25, facecolor=zonecolor)
				maxX = max(xvalues[i])
			if i>=1:
				ax2 = axis.twinx()
				ax2.plot(xvalues[i], yvalues[i], color=color[i])
				for tl in ax2.get_yticklabels():
					tl.set_color('%s' %color[i])
				maxXt = max(xvalues[i])
				if maxXt > maxX:
					maxX = maxXt
			axis.set_xlabel(xlabel[i])
			i+=1
		axis.set_xlim(0, maxX)

		if (len(xvalues)>1):
			axis.set_title("%s vs %s" %(ylabel[0],ylabel[1]))
		else:
			axis.set_title("%s" %(ylabel[0]))

		ylim_min, ylim_max = axis.get_ylim()
		if ylimits is not None:
			logging.debug("Using ylimits: %s" % str(ylimits))
			if ylimits[0] is not None:
				ylim_min = ylimits[0]
			if ylimits[1] is not None:
				ylim_max = ylimits[1]
			axis.set_ylim(ylim_min, ylim_max)


		logging.debug('<<')
		return {'y1_min': ylim_min, 'y1_max': ylim_max, 'y1_linewidth': linewidth}
