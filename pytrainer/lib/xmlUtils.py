# -*- coding: iso-8859-1 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net
# vud1@grupoikusnet.com
# Jakinbidea & Grupo Ikusnet Developer

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

import xml.dom.minidom 
from xml.dom.minidom import Node
from xml.dom.minidom import getDOMImplementation

class XMLParser:
	def __init__(self,filename = None):
		self.filename = filename
		self._load()

	def _load(self):
		try: 
			self.xmldoc = xml.dom.minidom.parse(self.filename) 
		except:
			self.xmldoc = None
			
	def setOptions(self,list_item, version):
		list_item.append(("version",version))
		self.createXMLFile(self,"pytraining",list_item)

	def getOptions(self):
		self._load()
		root = self.xmldoc.getElementsByTagName("pytraining")[0]
		list_options = {}
		list_keys = root.attributes.keys()
		for i in list_keys:
			value = self.getOption(i)
			list_options[i] = value
		return list_options	
	
	def getOption(self,option):
		print "this function is obsolete, use getValue instead"
		return self.getValue("pytraining",option)
		
	def setVersion(self,version):
		self.setValue("pytraining","version",version)

	def setValue(self,tagname,variable,value):
		root = self.xmldoc.getElementsByTagName(tagname)[0]
		if root.attributes.has_key(variable):
			root.attributes[variable]._set_value(value)
		else:
			root.setAttribute(variable,value)
		content = self.xmldoc.toprettyxml()
		self._saveFile(content)

	def getValue(self,tagname,variable):
		self._load()
		root = self.xmldoc.getElementsByTagName(tagname)[0]
		value = root.attributes[variable].value
		return value
	
	def getAllValues(self,tagname):	
		self._load()
		root = self.xmldoc.getElementsByTagName(tagname)
		retorno = []
		for i in root:
			retorno.append((i.attributes["variable"].value, i.attributes["value"].value))
		return retorno
	
	def createXMLFile(self,tag,list_options):
		impl = getDOMImplementation()
		self.xmldoc = impl.createDocument(None, tag, None)
		top_element = self.xmldoc.documentElement
		#top_element.appendChild(text)
		for option in list_options:
			var = option[0]
			value = option[1]
			attr = self.xmldoc.createAttribute(var)
			top_element.setAttributeNode(attr)
			top_element.attributes[var]._set_value(value)
		xmlcontent = self.xmldoc.toprettyxml()
		self._saveFile(xmlcontent)	

	def _saveFile(self,xmlcontent):
		out = open(self.filename, 'w')
		out.write(xmlcontent)
		out.close()

