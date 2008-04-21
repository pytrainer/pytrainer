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
import logging

from lib.system import checkConf
from lib.xmlUtils import XMLParser
from lib.ddbb import DDBB

class Profile:
	def __init__(self, data_path = None, parent = None):
		logging.debug(">>")
		self.parent = parent
		self.version = None
		self.data_path = data_path
		self.conf = checkConf()
		self.filename = self.conf.getValue("conffile")
		self.configuration = XMLParser(self.filename)
		logging.debug("<<")

	def isProfileConfigured(self):
		if self.conf.getConfFile():
			self.configuration = XMLParser(self.filename)
			self.ddbb = DDBB(self.configuration)
			return True

		else:
			#from gui.windowprofile import WindowProfile
			#profilewindow = WindowProfile(self.data_path, self)
			#profilewindow.run()
			self.createDefaultConf()
			return True

	def createDefaultConf(self):
		logging.debug(">>")
		conf_options = [
			("prf_name","annon"),
			("prf_gender",""),
			("prf_weight",""),
			("prf_height",""),
			("prf_age",""),
			("prf_ddbb","sqlite"),
			("prf_ddbbhost",""),
			("prf_ddbbname",""),
			("prf_ddbbuser",""),
			("prf_ddbbpass",""),]
		self.setProfile(conf_options)
		logging.debug("<<")

	def setVersion(self,version):
		logging.debug("--")
		self.version = version

	def setProfile(self,list_options):
		logging.debug(">>")
		logging.debug("Retrieving data from "+ self.filename)
		self.configuration = XMLParser(self.filename)
		list_options.append(("version",self.version))
		if not os.path.isfile(self.filename):
			self.configuration.createXMLFile("pytraining",list_options)
		for option in list_options:
			logging.debug("Adding "+option[0]+"|"+option[1])
			self.configuration.setValue("pytraining",option[0],option[1])
		self.ddbb = DDBB(self.configuration)
		logging.debug("<<")

	def getSportList(self):
		logging.debug("--")
		connection = self.ddbb.connect()
		if (connection == 1):
			logging.debug("retrieving sports info")
			return self.ddbb.select("sports","name,met,weight",None)
		else:
			return connection

	def addNewSport(self,sport,weight,met):
		logging.debug(">>")
		logging.debug("Adding new sport: "+sport+"|"+weight+"|"+met)
		sport = [sport,met,weight]
		self.ddbb.insert("sports","name,met,weight",sport)
		logging.debug("<<")
		
	def delSport(self,sport):
		logging.debug(">>")
		condition = "name=\"%s\"" %sport
		id_sport = self.ddbb.select("sports","id_sports",condition)[0][0]
		logging.debug("removing records from sport "+ sport)
		self.ddbb.delete("records","sport=\"%d\""%id_sport)
		logging.debug("removing sport "+ id_sport +" from DB")
		self.ddbb.delete("sports","id_sports=\"%d\""%id_sport)
		logging.debug("<<")
		
	def updateSport(self,oldnamesport,newnamesport,newmetsport,newweightsport):
		self.ddbb.update("sports","name,weight,met",[newnamesport,newmetsport,newweightsport],"name=\"%s\""%oldnamesport)
	
	def getSportInfo(self,namesport):
		return self.ddbb.select("sports","name,weight,met","name=\"%s\""%namesport)[0]
	
	def build_ddbb(self):
		logging.debug("--")
		self.ddbb.build_ddbb()

	def editProfile(self):
		logging.debug(">>")
		from gui.windowprofile import WindowProfile
		logging.debug("retrieving configuration data")
		list_options = self.configuration.getOptions()
		profilewindow = WindowProfile(self.data_path, self)
		logging.debug("setting data values")
		profilewindow.setValues(list_options)
		profilewindow.run()
		logging.debug("<<")
		
	def actualize_mainsportlist(self):
		logging.debug("--")
		self.parent.refreshMainSportList()

