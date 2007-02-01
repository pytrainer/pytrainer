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

from lib.xmlUtils import XMLParser
from lib.system import checkConf

from gui.windowplugins import WindowPlugins

class Plugins:
	def __init__(self, data_path = None):
		self.data_path=data_path
		self.conf = checkConf()
	
	def getActivePlugins(self):
		retorno = []
		for plugin in self.getPluginsList():
			if self.getPluginInfo(plugin[0])[2] == "1":
				retorno.append(plugin[0])
		return retorno	

	def loadPlugin(self,plugin):
		info = XMLParser(plugin+"/conf.xml")
		button = info.getValue("pytrainer-plugin","pluginbutton")
		name = info.getValue("pytrainer-plugin","name")
		print "Loading Plugin %s" %name
		return button,plugin
	
	def runPlugin(self,pathPlugin):
		info = XMLParser(pathPlugin+"/conf.xml")
		bin = info.getValue("pytrainer-plugin","executable")
		binnary = pathPlugin+"/"+bin
		params = ""
		for opt in self.getPluginConfParams(pathPlugin):
			if opt[0]!="status":
				params += "--%s %s" %(opt[0],opt[1])
		gpxfile = os.popen("%s %s" %(binnary,params)).read()
		gpxfile = gpxfile.replace("\n","")
		gpxfile = gpxfile.replace("\r","")
		return gpxfile
	
	def managePlugins(self):
		pluginsList = self.getPluginsList()
		windowplugins = WindowPlugins(self.data_path, self)
		windowplugins.setList(pluginsList)
		windowplugins.run()

	def getPluginsList(self):
		pluginsdir = self.data_path+"/plugins"
		pluginsList = []
		for plugin in os.listdir(pluginsdir):
			pluginxmlfile = pluginsdir+"/"+plugin+"/conf.xml"
			if os.path.isfile(pluginxmlfile):
				plugininfo = XMLParser(pluginxmlfile)
				name = plugininfo.getValue("pytrainer-plugin","name")
				description = plugininfo.getValue("pytrainer-plugin","description")
				pluginsList.append((pluginsdir+"/"+plugin,name,description))
	
		return pluginsList
	
	def getPluginInfo(self,pathPlugin):
		info = XMLParser(pathPlugin+"/conf.xml")
		name = info.getValue("pytrainer-plugin","name")
		description = info.getValue("pytrainer-plugin","description")
		code = info.getValue("pytrainer-plugin","plugincode")
		plugindir = self.conf.getValue("plugindir")
		if not os.path.isfile(plugindir+"/"+code+"/conf.xml"):
			status = 0
		else:
			info = XMLParser(plugindir+"/"+code+"/conf.xml")
			status = info.getValue("pytrainer-plugin","status")
		return name,description,status

	def getPluginConfParams(self,pathPlugin):
		info = XMLParser(pathPlugin+"/conf.xml")
		code = info.getValue("pytrainer-plugin","plugincode")
		plugindir = self.conf.getValue("plugindir")
		if not os.path.isfile(plugindir+"/"+code+"/conf.xml"):
			params = info.getAllValues("conf-values")
			params.append(("status","0"))
		else:
			prefs = info.getAllValues("conf-values")
			prefs.append(("status","0"))
			info = XMLParser(plugindir+"/"+code+"/conf.xml")
			params = []
			for pref in prefs:
				params.append((pref[0],info.getValue("pytrainer-plugin",pref[0])))
		return params

	def setPluginConfParams(self,pathPlugin,savedOptions):
		info = XMLParser(pathPlugin+"/conf.xml")
		code = info.getValue("pytrainer-plugin","plugincode")
		plugindir = self.conf.getValue("plugindir")+"/"+code
		if not os.path.isdir(plugindir):
			os.mkdir(plugindir)
		if not os.path.isfile(plugindir+"/conf.xml"):
			savedOptions.append(("status","0"))
		info = XMLParser(plugindir+"/conf.xml")
		info.createXMLFile("pytrainer-plugin",savedOptions)

	def loadExtension(self,pathPlugin):
		print "Loading extension: %s" %pathPlugin
		confParams = self.getExtensionConfParams(pathPlugin)
		extension = __init__(pathPlugin+"/main.py")
		object = extension.main(confParams)
		object.run()

	def getCodeConfValue(self,code,value):
		plugindir = self.conf.getValue("plugindir")
		info = XMLParser(plugindir+"/"+code+"/conf.xml")
		return info.getValue("pytrainer-plugin",value)
