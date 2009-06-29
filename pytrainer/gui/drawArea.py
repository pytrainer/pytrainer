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
from matplotlib.backends.backend_gtk import FigureCanvasGTK
from matplotlib.numerix import *
import matplotlib.pyplot as plt
from pylab import *
import logging

from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar

class DrawArea:
	def __init__(self, vbox = None, window = None):
		logging.debug('>>')
		self.figure = Figure(figsize=(6,4), dpi=72)
		self.axis = self.figure.add_subplot(111)
		self.vbox = vbox
		self.window = window
		self.canvas = FigureCanvasGTK(self.figure) # a gtk.DrawingArea
		#self.drawDefault()
		logging.debug('<<')

	def stadistics(self,type,xvalues,yvalues,xlabel,ylabel,title,color,zones=None):
		logging.debug('>>')	
		if len(xvalues[0]) < 1:
			#self.drawDefault()
			return False
		#logging.debug('xvalues: '+str(xvalues))
		#logging.debug('yvalues: '+str(yvalues))
		logging.info("Type: "+type+" | title: "+str(title)+" | col: "+str(color)+" | xlabel: "+str(xlabel)+" | ylabel: "+str(ylabel))
		if type == "bars":
			self.drawBars(xvalues,yvalues,xlabel,ylabel,title,color)
		elif type == "plot":
			self.drawPlot(xvalues,yvalues,xlabel,ylabel,title,color,zones)
		elif type == "pie":
			self.drawPie(xvalues,yvalues,xlabel,ylabel,title,color,zones)
		logging.debug('<<')

	def drawBars(self,xvalues,yvalues,xlabel,ylabel,title,color):
		logging.debug('>>')		
		self.canvas.destroy()
		self.vbox.remove(self.canvas)
		self.figure = Figure(figsize=(6,4), dpi=72)
        	self.canvas = FigureCanvasGTK(self.figure) # a gtk.DrawingArea
		self.axis.clear()
		width = 1
		i=0
		for value in xvalues:
			if len(xvalues) == 1:
				self.axis = self.figure.add_subplot(111)
			else:
				self.axis =self.figure.add_subplot(211 + i)
			self.axis.set_xlim(-width,len(xvalues[i]))
			self.axis.set_xlabel(xlabel[i])
			self.axis.set_ylabel(ylabel[i])
			self.axis.set_title(title[i])		
			p1 = self.axis.bar(xvalues[i], yvalues[i], width, color=color[i])
			i+=1
		
		self.canvas = FigureCanvasGTK(self.figure) # a gtk.DrawingArea
		self.canvas.show()
		self.vbox.pack_start(self.canvas, True, True)
		logging.debug('<<')

	def drawPlot(self,xvalues,yvalues,xlabel,ylabel,title,color,zones=None):
		logging.debug('>>')  
		#self.canvas.destroy()
		#self.vbox.remove(self.canvas)
		for child in self.vbox.get_children():
			if self.vbox.get_children()[0] != child:
				self.vbox.remove(child)

		#self.figure = plt.figure()
		self.figure = Figure()
		self.axis.clear()
		i = 0
		for value in xvalues:
			if i==0:
				self.axis = self.figure.add_subplot(111)
				self.axis.plot(xvalues[i],yvalues[i], color=color[i])
				self.axis.set_xlabel(xlabel[i])
				#self.axis.set_ylabel(ylabel[i],color=color[i])
				if (len(xvalues)>1):
					self.axis.set_title("%s vs %s" %(ylabel[0],ylabel[1]))
				else:
					self.axis.set_title("%s" %(ylabel[0]))
					
				self.axis.grid(True)
				for tl in self.axis.get_yticklabels():
    					tl.set_color('%s' %color[i])
			if i==1:
				ax2 = self.axis.twinx()
				ax2.plot(xvalues[i], yvalues[i], color=color[i])
				for tl in ax2.get_yticklabels():
    					tl.set_color('%s' %color[i])
				self.axis.set_xlabel(xlabel[i])
		#		axis2 = self.axis.twinx()
		#		axis2.plot(xvalues[i],yvalues[i], color=color[i])
				#axis2.set_ylabel(ylabel[i],color=color[i])
			#else:
			#	self.axis =self.figure.add_subplot(211 + i)
			i+=1


		#if zones!=None:	
		#	for zone in zones:	
		#		p = self.axis.axhspan(zone[0], zone[1], facecolor=zone[2], alpha=0.5, label=zone[3])
		#	l = self.axis.legend(loc='lower right')
		self.canvas = FigureCanvasGTK(self.figure) # a gtk.DrawingArea
		self.canvas.show()
		self.vbox.pack_start(self.canvas, True, True)
		toolbar = NavigationToolbar(self.canvas, self.window)
		self.vbox.pack_start(toolbar, False, False)
		if title[0] == 'Stage Profile':
			self.figure.savefig('/tmp/stage.png', dpi=75)
		if title[0] == 'Heart Rate':
			self.figure.savefig('/tmp/hr.png', dpi=75)
		logging.debug('<<')
	
	def drawPie(self,xvalues,yvalues,xlabel,ylabel,title,color,zones=None):
		logging.debug('>>')
		self.canvas.destroy()
		self.vbox.remove(self.canvas)
		self.figure = Figure(figsize=(6,4), dpi=72)
		#self.canvas = FigureCanvasGTK(self.figure) # a gtk.DrawingArea
		#self.axis.clear()
		self.axis = self.figure.add_subplot(111)

		labels = ["rest"]
		colors = ["#ffffff"]
		frac0 = 0
		frac1 = 0
		frac2 = 0
		frac3 = 0
		frac4 = 0
		frac5 = 0
		for zone in zones:
			labels.append(zone[3])
			colors.append(zone[2])
	
		for value in yvalues[0]:
			if value < zones[4][0]:
				frac0+=1
			elif value > zones[4][0] and value < zones[4][1]:
				frac1+=1
			elif value > zones[3][0] and value < zones[3][1]:
				frac2+=1
			elif value > zones[2][0] and value < zones[2][1]:
				frac3+=1
			elif value > zones[1][0] and value < zones[1][1]:
				frac4+=1
			elif value > zones[0][0] and value < zones[0][1]:
				frac5+=1
			
		fracs = [frac0,frac1,frac2,frac3,frac4, frac5]
		explode=(0, 0, 0, 0,0,0)
		self.axis.pie(fracs, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True)

		self.canvas = FigureCanvasGTK(self.figure) # a gtk.DrawingArea
		self.canvas.show()
		self.vbox.pack_start(self.canvas, True, True)
		logging.debug('<<')

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
		self.vbox.pack_start(self.canvas, True, True)
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

