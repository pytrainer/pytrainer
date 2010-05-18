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

import gtkmozembed
import logging
import os

from pytrainer.lib.fileUtils import fileUtils

class MapViewer:
	def __init__(self, data_path = None, pytrainer_main=None, box=None):
		logging.debug(">>")
		self.data_path = data_path
		self.pytrainer_main = pytrainer_main
		if box is None:
			logging.debug("Display box (%s) is None" % ( str(box)))
			return
		self.box = box
		gtkmozembed.set_profile_path("/tmp", "foobar") # http://faq.pygtk.org/index.py?req=show&file=faq19.018.htp  #TODO FIX???
		self.moz = gtkmozembed.MozEmbed()
		self.pack_box()
		logging.debug("<<")

	def pack_box(self):
		logging.debug(">>")
		self.box.pack_start(self.moz, True, True)
		self.box.show_all()
		logging.debug("<<")

	def display_map(self, htmlfile=None):
		logging.debug(">>")
		if htmlfile is None:
			htmlfile = self.createErrorHtml()
		self.moz.load_url("file://%s" % (htmlfile))
		#self.box.show_all()
		logging.debug("<<")

	def createErrorHtml(self):
		logging.debug(">>")
		htmlfile = "%s/error.html" % (self.pytrainer_main.profile.tmpdir)
		content = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"  xmlns:v="urn:schemas-microsoft-com:vml">
<head>
<body>
No HTML file supplied to display
</body>
</html>
		'''
		file = fileUtils(htmlfile,content)
		file.run()
		logging.debug("<<")
		return htmlfile
