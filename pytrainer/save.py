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

from lib.fileUtils import fileUtils
from gui.filechooser import FileChooser

class Save:
	def __init__(self, data_path = None, record = None):
		self.record = record
		self.data_path = data_path

	def run(self):
		self.filewindow = FileChooser(self.data_path, self, "savecsvfile")
		self.filewindow.run()
	
	def savecsvfile(self):
		filename = self.filewindow.filename
		records = self.record.getAllrecord()
		content = ""
		for record in records:
			line = ""
			for data in record:
				data = "%s" %data
				data.replace(",", " ")
				line += ", %s" %data
			content += "%s \n" %line
		file = fileUtils(filename,content)
		file.run()
		


