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
		self.y_values = []
		self.linewidth = 1
		self.linecolor = '#ff0000'
		self.max_x_value = None
		self.min_x_value = None
		self.max_y_value = None
		self.min_y_value = None
		logging.debug('<<')

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
x min max: %s %s
y min max: %s %s
x values: %s
y values: %s''' % (self.title,
	self.ylabel,
	self.xlabel,
	self.linewidth,
	self.linecolor,
	str(self.min_x_value), str(self.max_x_value),
	str(self.min_y_value), str(self.max_y_value),
	str(self.x_values),
	str(self.y_values)
	)

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




