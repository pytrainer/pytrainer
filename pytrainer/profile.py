# -*- coding: iso-8859-1 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net
# Modified by dgranda

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

import os, sys
import logging

from lxml import etree
from lib.ddbb import DDBB

class Profile:
	def __init__(self, data_path = None, parent = None):
		logging.debug(">>")
		self.pytrainer_main = parent
		self.data_path = data_path
		self.xml_tree = None
		self.home = None
		self.tmpdir = None
		self.confdir = None
		self.conffile = None
		self.gpxdir = None
		self.extensiondir = None
		self.plugindir = None
		#Set configuration parameters 
		self._setHome()
		self._setConfFiles()
		self._setTempDir()
		self._setExtensionDir()
		self._setPluginDir()
		self._setGpxDir()
		
		#Clear temp dir
		logging.debug("clearing tmp directory %s" % self.tmpdir)
		self._clearTempDir()
		
		#Profile Options and Defaults
		self.profile_options = {
			"prf_name":"default",
			"prf_gender":"",
			"prf_weight":"",
			"prf_height":"",
			"prf_age":"",
			"prf_ddbb":"sqlite",
			"prf_ddbbhost":"",
			"prf_ddbbname":"",
			"prf_ddbbuser":"",
			"prf_ddbbpass":"",
			"version":"0.0",
			"DB_version":"0",
			"prf_us_system":"False",
			"prf_hrzones_karvonen":"False",
			"prf_maxhr":"",
			"prf_minhr":"",
			"auto_launch_file_selection":"False",
			"import_default_tab":"0",
			}

		#Parse pytrainer configuration file
		self.config_file = self.conffile
		self.configuration = self._parse_config_file(self.config_file)
		logging.debug("Configuration retrieved: "+str(self.configuration))
		self.pytrainer_main.ddbb = DDBB(self, pytrainer_main=self.pytrainer_main)
		logging.debug("<<")

	def _setHome(self):
		if sys.platform == "linux2":
			variable = 'HOME'
		elif sys.platform == "win32":
			variable = 'USERPROFILE'
		else:
			print "Unsupported sys.platform: %s." % sys.platform
			sys.exit(1)
		self.home = os.environ[variable]
    
	def _setTempDir(self):
		self.tmpdir = self.confdir+"/tmp"
		if not os.path.isdir(self.tmpdir):
			os.mkdir(self.tmpdir)

	def _clearTempDir(self):
		"""Function to clear out the tmp directory that pytrainer uses
			will only remove files
		"""
		if not os.path.isdir(self.tmpdir):
			return
		else:
			files = os.listdir(self.tmpdir)
			for name in files:
				fullname = (os.path.join(self.tmpdir, name))
				if os.path.isfile(fullname):
					os.remove(os.path.join(self.tmpdir, name))
   
	def _setConfFiles(self):
		if sys.platform == "win32":
			self.confdir = self.home+"/pytrainer"
		elif sys.platform == "linux2":
			self.confdir = self.home+"/.pytrainer"
		else:
			print "Unsupported sys.platform: %s." % sys.platform
			sys.exit(1)
		self.conffile = self.confdir+"/conf.xml"
		if not os.path.isdir(self.confdir):
			os.mkdir(self.confdir)
	
	def _setGpxDir(self):
		self.gpxdir = self.confdir+"/gpx"
		if not os.path.isdir(self.gpxdir):
			os.mkdir(self.gpxdir)
	
	def _setExtensionDir(self):
		self.extensiondir = self.confdir+"/extensions"
		if not os.path.isdir(self.extensiondir):
			os.mkdir(self.extensiondir)
	
	def _setPluginDir(self):
		self.plugindir = self.confdir+"/plugins"
		if not os.path.isdir(self.plugindir):
			os.mkdir(self.plugindir)

	def getConfFile(self):
		if not os.path.isfile(self.conffile):
			return False
		else:
			return self.conffile

	def _parse_config_file(self, config_file):
		'''
		Parse the xml configuration file and convert to a dict
		
		returns: dict with option as key
		'''
		if config_file is None:
			logging.error("Configuration file value not set")
		elif not os.path.isfile(config_file):
			logging.error("Configuration '%s' file does not exist" % config_file)
			logging.info("No profile found. Creating default one")
			self.setProfile(self.profile_options)
		else:
			logging.debug("Attempting to parse content from "+ config_file)
			try:
				parser = etree.XMLParser(encoding='UTF8', recover=True)
				self.xml_tree = etree.parse(config_file, parser=parser)
				#TODO check here for empty file....
				# Checks if configuration file is empty
				#if self.configuration.xmldoc is None:
				#	logging.error("Seems no data available in local configuration file: "+self.filename+", please check")
				#	logging.error("Fatal error, exiting")
				#	exit(-3)
				#Have a populated xml tree, get pytraining node (root) and convert it to a dict
				pytraining_tag = self.xml_tree.getroot()
				config = {}
				config_needs_update = False
				for key, default in self.profile_options.items():
					value = pytraining_tag.get(key)
					#If property is not found, set it to the default
					if value is None:
						config_needs_update = True 
						value = default
					config[key] = value
				#Added a property, so update config 
				if config_needs_update:
					self.setProfile(config)
				return config
			except Exception as e:
				logging.error("Error parsing file: %s. Exiting" % config_file)
				logging.error(str(e))
		logging.error("Fatal error, exiting")
		exit(-3)
		
	def getValue(self, tag, variable):
		if tag != "pytraining":
			print "ERROR - pytraining is the only profile tag supported"
			return None
		elif not self.configuration.has_key(variable):
			return None
		return self.configuration[variable]
		
	def setValue(self, tag, variable, value, delay_write=False):
		logging.debug(">>")
		if tag != "pytraining":
			print "ERROR - pytraining is the only profile tag supported"
		logging.debug("Setting %s to %s" % (variable, value))  
		self.xml_tree.getroot().set(variable, value.decode('utf-8'))
		if not delay_write:
			logging.debug("Writting...")
			self.xml_tree.write(self.config_file, xml_declaration=True, encoding='UTF-8')
		logging.debug("<<")

	def setProfile(self,list_options):
		logging.debug(">>")
		for option, value in list_options.items():
			logging.debug("Adding "+option+"|"+value)
			self.setValue("pytraining",option,value,delay_write=True)
		self.xml_tree.write(self.config_file, xml_declaration=True, encoding='UTF-8') 
		logging.debug("<<")

	def getSportList(self):
		logging.debug("--")
		connection = self.pytrainer_main.ddbb.connect()
		if (connection == 1):
			logging.debug("retrieving sports info")
			return self.pytrainer_main.ddbb.select("sports","name,met,weight,id_sports",None)
		else:
			return connection

	def addNewSport(self,sport,met,weight):
		"""31.08.2008 - dgranda
		It adds a new sport.
		arguments:
			sport: sport's name 
			met:
			weight:
		returns: id_sports from new sport"""
		logging.debug(">>")
		logging.debug("Adding new sport: "+sport+"|"+weight+"|"+met)
		sport = [sport,met,weight]
		self.pytrainer_main.ddbb.insert("sports","name,met,weight",sport)
		sport_id = self.pytrainer_main.ddbb.select("sports","id_sports","name=\"%s\"" %(sport))
		logging.debug("<<")
		return sport_id
		
	def delSport(self,sport):
		logging.debug(">>")
		condition = "name=\"%s\"" %sport
		id_sport = self.pytrainer_main.ddbb.select("sports","id_sports",condition)[0][0]
		logging.debug("removing records from sport "+ sport + " (id_sport: "+str(id_sport)+")")
		self.pytrainer_main.ddbb.delete("records","sport=\"%d\""%id_sport)
		self.pytrainer_main.ddbb.delete("sports","id_sports=\"%d\""%id_sport)
		logging.debug("<<")
		
	def updateSport(self,oldnamesport,newnamesport,newmetsport,newweightsport):
		logging.debug("--")
		self.pytrainer_main.ddbb.update("sports","name,met,weight",[newnamesport,newmetsport,newweightsport],"name=\"%s\""%oldnamesport)
	
	def getSportInfo(self,namesport):
		logging.debug("--")
		return self.pytrainer_main.ddbb.select("sports","name,met,weight","name=\"%s\""%namesport)[0]
	
	def build_ddbb(self):
		logging.debug("--")
		self.pytrainer_main.ddbb.build_ddbb()

	def editProfile(self):
		logging.debug(">>")
		from gui.windowprofile import WindowProfile
		logging.debug("retrieving configuration data")
		#Refresh configuration
		self.configuration = self._parse_config_file(self.config_file)
		profilewindow = WindowProfile(self.data_path, self, pytrainer_main=self.pytrainer_main)
		logging.debug("setting data values")
		profilewindow.setValues(self.configuration)
		profilewindow.run()
		logging.debug("<<")
		
	def actualize_mainsportlist(self):
		logging.debug("--")
		self.pytrainer_main.refreshMainSportList()

