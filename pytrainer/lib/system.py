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
import sys

class checkConf:
	def __init__(self):
		self.home = None
		self.tmpdir = None
		self.confdir = None
		self.conffile = None
            	self.gpxdir = None
		self.extensiondir = None
		self.plugindir = None

		self._setHome()
		self._setTempDir()
		self._setConfFiles()
		self._setExtensionDir()
		self._setPluginDir()
		self._setGpxDir()

    	def _setHome(self):
        	if sys.platform == "linux2":
            		variable = 'HOME'
            	elif sys.platform == "win32":
			variable = 'USERPROFILE'

        	self.home = os.environ[variable]
    
    	def _setTempDir(self):
        	if sys.platform == "win32":
            		self.tmpdir = "C:/backup"
        	elif sys.platform == "linux2":
            		self.tmpdir = "/tmp/virtual_dir"
        
        	if not os.path.isdir(self.tmpdir):
            		os.mkdir(self.tmpdir)
       
      	def _setConfFiles(self):
        	if sys.platform == "win32":
            		self.confdir = self.home+"/pytrainer"
			self.conffile = self.confdir+"/conf.xml"
        	elif sys.platform == "linux2":
            		self.confdir = self.home+"/.pytrainer"
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

	def getValue(self,variable):
		method = getattr(self, variable)
		return method
		
