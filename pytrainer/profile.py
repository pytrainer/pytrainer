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

import os

from lib.system import checkConf
from lib.xmlUtils import XMLParser
from lib.ddbb import DDBB

class Profile:
	def __init__(self, data_path = None, parent = None):
		self.parent = parent
		self.version = None
		self.data_path = data_path
		self.conf = checkConf()
		self.filename = self.conf.getValue("conffile")

	def isProfileConfigured(self):
		if self.conf.getConfFile():
			self.configuration = XMLParser(self.filename)
			self.ddbb = DDBB(self.configuration)
			return True

		else:
			from gui.windowprofile import WindowProfile
			profilewindow = WindowProfile(self.data_path, self)
			profilewindow.run()

	def setVersion(self,version):
		self.version = version

	def setProfile(self,list_options):
		self.configuration = XMLParser(self.filename)
		list_options.append(("version",self.version))
		if not os.path.isfile(self.filename):
			self.configuration.createXMLFile("pytraining",list_options)
		for option in list_options:
			self.configuration.setValue("pytraining",option[0],option[1])
		self.ddbb = DDBB(self.configuration)

	def getSportList(self):
		connection = self.ddbb.connect()
		if (connection == 1):
			return self.ddbb.select("sports","name",None)
		else:
			return connection

	def addNewSport(self,sport):
		sport = [sport]
		self.ddbb.insert("sports","name",sport)
		
	def delSport(self,sport):
		condition = "name=\"%s\"" %sport
		id_sport = self.ddbb.select("sports","id_sports",condition)[0][0]
		self.ddbb.delete("records","sport=\"%d\""%id_sport)
		self.ddbb.delete("sports","id_sports=\"%d\""%id_sport)
		
	def updateSport(self,oldnamesport,newnamesport):
		self.ddbb.update("sports","name",[newnamesport],"name=\"%s\""%oldnamesport)
	
	def build_ddbb(self):
		self.ddbb.build_ddbb()

	def editProfile(self):
		from gui.windowprofile import WindowProfile
		list_options = self.configuration.getOptions()
		profilewindow = WindowProfile(self.data_path, self)
		profilewindow.setValues(list_options)
		profilewindow.run()
		
	def actualize_mainsportlist(self):
		self.parent.refreshMainSportList()

