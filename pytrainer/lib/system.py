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
		self._setConfFiles()
		self._setTempDir()
		self._setExtensionDir()
		self._setPluginDir()
		self._setGpxDir()

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

	def clearTempDir(self):
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

	def getValue(self,variable):
		method = getattr(self, variable)
		return method
