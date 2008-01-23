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
matplotlib.use('GTK')
from matplotlib.figure import Figure
from matplotlib.axes import Subplot
from matplotlib.backends.backend_gtk import FigureCanvasGTK, NavigationToolbar
from matplotlib.numerix import *
from pylab import *

class DrawArea:
	def __init__(self, vbox = None):
		self.figure = Figure(figsize=(6,4), dpi=72)
        	self.axis = self.figure.add_subplot(111)
		self.vbox = vbox
        	self.canvas = FigureCanvasGTK(self.figure) # a gtk.DrawingArea
		self.drawDefault()

	def stadistics(self,type,xvalues,yvalues,xlabel,ylabel,title,color,zones=None):
		if len(xvalues[0]) < 1:
			self.drawDefault()
			return False
		if type == "bars":
			self.drawBars(xvalues,yvalues,xlabel,ylabel,title,color)
		elif type == "plot":
			self.drawPlot(xvalues,yvalues,xlabel,ylabel,title,color,zones)

	def drawBars(self,xvalues,yvalues,xlabel,ylabel,title,color):
                self.canvas.destroy()
		self.figure = Figure(figsize=(6,4), dpi=72)
        	self.canvas = FigureCanvasGTK(self.figure) # a gtk.DrawingArea
		self.axis.clear()
		width = 1
		for i in range(0,len(xvalues)):
			if len(xvalues) == 1:
        			self.axis = self.figure.add_subplot(111)
			else:
        			self.axis =self.figure.add_subplot(211 + i)
                	self.axis.set_xlim(-width,len(xvalues[i]))
			self.axis.set_xlabel(xlabel[i])
			self.axis.set_ylabel(ylabel[i])
			self.axis.set_title(title[i])
		
                	p1 = self.axis.bar(xvalues[i], yvalues[i], width, color=color[i])
                p = axvspan(1.25, 100.55, facecolor='g', alpha=0.5)
		self.canvas = FigureCanvasGTK(self.figure) # a gtk.DrawingArea
                self.canvas.show()
                self.vbox.pack_start(self.canvas, True, True)

	def drawPlot(self,xvalues,yvalues,xlabel,ylabel,title,color,zones=None):
                self.canvas.destroy()
		self.figure = Figure(figsize=(6,4), dpi=72)
        	self.canvas = FigureCanvasGTK(self.figure) # a gtk.DrawingArea
		self.axis.clear()
		i = 0
		for value in xvalues:
			if len(xvalues) == 1:
        			self.axis = self.figure.add_subplot(111)
			else:
        			self.axis =self.figure.add_subplot(211 + i)
			self.axis.set_xlabel(xlabel[i])
			self.axis.set_ylabel(ylabel[i])
			self.axis.set_title(title[i])
        		self.axis.grid(True)
                	self.axis.plot(xvalues[i],yvalues[i], color=color[i])
			i+=1
		if zones!=None:	
			for zone in zones:	
                		p = self.axis.axhspan(zone[0], zone[1], facecolor=zone[2], alpha=0.5, label=zone[3])
		l = self.axis.legend(loc='lower right')
		self.canvas = FigureCanvasGTK(self.figure) # a gtk.DrawingArea
		self.canvas.show()
                self.vbox.pack_start(self.canvas, True, True)
	
	def drawDefault(self):
		self.axis.clear()
        	self.axis=self.figure.add_subplot(111)
        	self.axis.set_xlabel('Yepper')
        	self.axis.set_ylabel('Flabber')
        	self.axis.set_title('An Empty Graph')
        	self.axis.grid(True)
                self.canvas.destroy()
        	self.canvas = FigureCanvasGTK(self.figure) # a gtk.DrawingArea
        	self.canvas.show()
        	self.vbox.pack_start(self.canvas, True, True)

	def fill_over(self, ax, x, y, val, color, over=True):
    		"""
    		Plot filled x,y for all y over val
    		if over = False, fill all areas < val
    		"""
    		ybase = asarray(y)-val
    		crossings = nonzero(less(ybase[:-1] * ybase[1:],0))

    		if ybase[0]>=0: fillon = over
    		else:           fillon = not over


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

