# -*- coding: iso-8859-1 -*-

#Copyright (C)

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
from lxml import etree

class xmlValidator():
	def validateXSL(self, filename, xslfile):
		try:
			doc = etree.parse(filename)
			xsl_doc = etree.parse(xslfile)
			xsl = etree.XMLSchema(xsl_doc)
		except:
			logging.error("Error attempting to parse %s or %s" % (filename, xslfile))
			return False
		if xsl.validate(doc):
			logging.info("%s validates against %s" % (filename, xslfile))
			print "%s validates against %s" % (filename, xslfile)
			return True
		else:
			logging.info("%s did not validate against %s" % (filename, xslfile))
			print "%s did not validate against %s" % (filename, xslfile)
			return False
