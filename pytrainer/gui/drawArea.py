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
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvasGTK
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
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

	def stadistics(self,type,xvalues,yvalues,xlabel,ylabel,title,color=None,zones=None):
		logging.debug('>>')	
		if len(xvalues[0]) < 1:
			#self.drawDefault()
			return False
		#logging.debug('xvalues: '+str(xvalues))
		#logging.debug('yvalues: '+str(yvalues))
		#logging.debug("Type: "+type+" | title: "+str(title)+" | col: "+str(color)+" | xlabel: "+str(xlabel)+" | ylabel: "+str(ylabel))
		if type == "bars":
			self.drawBars(xvalues,yvalues,xlabel,ylabel,title,color)
		elif type == "plot":
			self.drawPlot(xvalues,yvalues,xlabel,ylabel,title,color,zones)
		elif type == "pie":
			self.drawPie(xvalues,yvalues,xlabel,ylabel,title,color,zones)
		logging.debug('<<')

	def drawBars(self,xvalues,yvalues,xlabel,ylabel,title,color):
		logging.debug('>>')	
		logging.debug("Type: bars | title: "+str(title)+" | col: "+str(color)+" | xlabel: "+str(xlabel)+" | ylabel: "+str(ylabel))
		self.removeVboxChildren()	
		figure = Figure(figsize=(6,4), dpi=72)
		numCols=len(xvalues[0])
		xmod = 0.4
		self.showGraph=False
		axis = figure.add_subplot(111)

		if len(xvalues) == 1: #One axis
			barWidth = 0.8
			barOffset = 0.1
		elif len(xvalues) == 2: #Twin axes
			barWidth = 0.4
			barOffset = 0.1
		else: #Error
			return

		axis.set_xlabel(xlabel[0])
		axis.set_ylabel(ylabel[0])
		xvals = [x+barOffset for x in range(0, numCols)]
		yvals = [0] * numCols
		for i in range(0, numCols):
			yval = yvalues[0][i]
			if float(yval) > 0.0:
				self.showGraph=True
			else:
				yval = self.NEARLY_ZERO
			yvals[i] = yval
		if self.showGraph:
			axis.bar(xvals, yvals, barWidth, color=color[0], align='edge')		
		else:	#Only zero results
			pass

		axis.grid(True)
		axis.set_title("%s" %(title[0]))
		for tl in axis.get_yticklabels():
			tl.set_color('%s' %color[0])

		if len(xvalues) == 2: #Display twin axis
			ax2 = axis.twinx()
			xvals = [x+barOffset+barWidth for x in range(0, numCols)]
			for i in range(0, numCols):
				yval = yvalues[1][i]
				if float(yval) > 0.0:
					self.showGraph=True
				else:
					yval = self.NEARLY_ZERO
				yvals[i] = yval
			if self.showGraph:
				ax2.bar(xvals, yvals, barWidth, color=color[1], align='edge')
				ax2.set_ylabel(ylabel[1])
			else:	#Only zero results
				pass
			for tl in ax2.get_yticklabels():
   				tl.set_color('%s' %color[1])
			axis.set_title("%s vs %s" %(title[0],title[1]))

		tickLocations = [x+0.5 for x in xrange(0, numCols)]
		axis.set_xticks(tickLocations)
		axis.set_xticklabels(xvalues[0])
		axis.set_xlim(0, numCols)
		
		canvas = FigureCanvasGTK(figure) # a gtk.DrawingArea
		canvas.show()
		self.vbox.pack_start(canvas, True, True)
		#toolbar = NavigationToolbar(canvas, self.window)
		#self.vbox.pack_start(toolbar, False, False)

		for child in self.vbox.get_children():
			logging.debug('Child available: '+str(child))

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

	def drawStackedBars(self,xvalues,yvalues,ylabel,title, valuesAreTime=False):
		'''function to draw stacked bars
			xvalues needs to be a list of lists of strings, e.g. [0]["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
			yvalues needs to be a list of dicts e.g. [0]{'Kayak': {'Tue': 10.08, 'Fri': 17.579999999999998, 'Thu': 15.66, 'Sat': 30.619999999999997}, {'Run': {'Mon': 9.65, 'Sun': 15.59}}
		'''
		#TODO tidy
		logging.debug('>>')	
		logging.debug("Title: %s", (title, ))
		logging.debug("X values received: %s", str(xvalues))
		logging.debug("Y values received: %s", str(yvalues))
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

		keys = yvalues[0].keys() # days of the week
		numRows = len(keys)
		numCols = len(xvalues[0])
		if numRows == 0:
			return
		width = .8
		figure = plt.figure(figsize=(6,4), dpi=72) 
		axis = plt.subplot(111)

		ybottoms = [0] * numCols
		yheights = [0] * numCols
		inds = xrange(0, numCols)
		xvals = [x+barOffset for x in range(0, numCols)]
		cellText = []
		self.showGraph=False

		#Display first axis
		for key in keys:
			logging.debug("Day of the week: %s", str(key))
			for ind in inds:
				ybottoms[ind] += yheights[ind]
				yheights[ind] = 0 #Zero heights
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
			else:	#Only zero results
				pass
		axis.set_xticklabels('' * len(xvalues[0]))
		axis.set_ylabel(ylabel[0])
		if len(xvalues) == 1:
			plt.title(title[0])
			axis.legend(loc=0)

		logging.debug("X values first axis: %s", str(xvals))
		logging.debug("Y values first axis: %s", str(yheights))

		#Display twin axis
		if len(xvalues) == 2: 
			self.showGraph=False
			ax2 = axis.twinx()
			keys = yvalues[1].keys()
			ybottoms = [0] * numCols
			yheights = [self.NEARLY_ZERO] * numCols
			for key in keys:
				for ind in inds:
					ybottoms[ind] += yheights[ind]
					yheights[ind] = 0.0 #Zero heights
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
					if textToAdd is not ' ':
						row = keys.index(key)
						col = index
						cellText[row][col] += " | %s" % (self.fmtTableText(height, valuesAreTime[1]))
						#print "Would add %s to %s %s" % (self.fmtTableText(height, valuesAreTime[1]), index, keys.index(key))						
				if self.showGraph:
					xvals = [x+barOffset+barWidth for x in range(0, numCols)]
					#print "ax2", xvals, yheights, ybottoms
					ax2.bar(xvals, yheights, bottom=ybottoms, width=barWidth, color=color,  align='edge', label=key)
				else:	#Only zero results
					ax2.bar(xvals, [0]*numCols, bottom=[0]*numCols, width=barWidth, color=color,  align='edge', label=key)
					pass
			ax2.set_xticklabels('' * len(xvalues[1]))
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
		self.vbox.pack_start(canvas, True, True)
		#toolbar = NavigationToolbar(canvas, self.window)
		#self.vbox.pack_start(toolbar, False, False)

		for child in self.vbox.get_children():
			logging.debug('Child available: '+str(child))

		logging.debug('<<')

	def drawPlot(self,xvalues,yvalues,xlabel,ylabel,title,color,zones=None,xzones=None):
		logging.debug('>>')  
		logging.debug("Type: plot | title: "+str(title)+" | col: "+str(color)+" | xlabel: "+str(xlabel)+" | ylabel: "+str(ylabel))
		logging.debug('xlabel: '+str(xlabel)+' | ylabel: '+str(ylabel)+' | title: '+str(title))
		self.removeVboxChildren()
		figure = Figure()
		figure.clf()
		i = 0
		for value in xvalues:
			if i<1:
				axis = figure.add_subplot(111)
				axis.plot(xvalues[i],yvalues[i], color=color[i])
					
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
		ylim = axis.get_ylim()

		canvas = FigureCanvasGTK(figure) # a gtk.DrawingArea
		canvas.show()
		self.vbox.pack_start(canvas, True, True)
		toolbar = NavigationToolbar(canvas, self.window)
		self.vbox.pack_start(toolbar, False, False)
		
		for child in self.vbox.get_children():
			logging.debug('Child available: '+str(child))
		
		logging.debug('<<')
		return ylim
	
	def drawPie(self,xvalues,yvalues,xlabel,ylabel,title,color,zones=None):
		logging.debug('>>')
		logging.debug("Type: pie | title: "+str(title)+" | col: "+str(color)+" | xlabel: "+str(xlabel)+" | ylabel: "+str(ylabel))
		self.removeVboxChildren()
		figure = Figure(figsize=(6,4), dpi=72)
		axis = figure.add_subplot(111)

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
		axis.pie(fracs, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True)

		canvas = FigureCanvasGTK(figure) # a gtk.DrawingArea
		canvas.show()

		for child in self.vbox.get_children():
			logging.debug('Child available: '+str(child))

		self.vbox.pack_start(canvas, True, True)
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

	def removeVboxChildren(self):
		''' function to delete vbox children so that multiple graphs do not appear
			there must a better way to do this - pyplot?
		'''
		logging.debug('>>')
		#Tidy up draw areas	
		vboxChildren = self.vbox.get_children()
		logging.debug('Vbox has %d children %s' % (len(vboxChildren), str(vboxChildren) ))
		# ToDo: check why vertical container is shared
		for child in vboxChildren:
			#Remove all FigureCanvasGTK and NavigationToolbar2GTKAgg to stop double ups of graphs
			if isinstance(child, matplotlib.backends.backend_gtkagg.FigureCanvasGTK) or isinstance(child, matplotlib.backends.backend_gtkagg.NavigationToolbar2GTKAgg):
				logging.debug('Removing child: '+str(child))
				self.vbox.remove(child)
		logging.debug('<<')
