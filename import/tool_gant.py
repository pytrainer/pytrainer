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

import logging
import os, sys, commands
import StringIO
from lxml import etree
import dateutil.parser
from dateutil.tz import * # for tzutc()

from pytrainer.lib.system import checkConf

class gant():
	def __init__(self, parent = None, data_path = None):
		self.parent = parent
		self.conf = checkConf()
		self.tmpdir = self.conf.getValue("tmpdir")
		self.main_data_path = data_path
		self.data_path = os.path.dirname(__file__)

	def getName(self):
		return _("Gant")

	def getVersion(self):
		outstatus = commands.getstatusoutput('which gant')
		if outstatus[0] == 0: #Found gant in path 
			path = outstatus[1]
			return path
		else:
			return None
		return None

	def getSourceLocation(self):
		return "http://cgit.get-open.com/cgit.cgi/gant/"

	def deviceExists(self):
		return True

	def isPresent(self):
		if self.getVersion():
			return True
		else:
			return False
	
	def getDateTime(self, time_):
		# Time can be in multiple formats
		# - zulu 			2009-12-15T09:00Z
		# - local ISO8601	2009-12-15T10:00+01:00
		if time_ is None or time_ == "":
			return (None, None)
		dateTime = dateutil.parser.parse(time_)
		timezone = dateTime.tzname()
		if timezone == 'UTC': #got a zulu time
			local_dateTime = dateTime.astimezone(tzlocal()) #datetime with localtime offset (from OS)
		else:
			local_dateTime = dateTime #use datetime as supplied
		utc_dateTime = dateTime.astimezone(tzutc()) #datetime with 00:00 offset
		return (utc_dateTime,local_dateTime)
