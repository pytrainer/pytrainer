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

from SimpleGladeApp import SimpleGladeApp

class Warning(SimpleGladeApp):
	def __init__(self, data_path = None, okmethod = None, okparams = None, cancelmethod = None, cancelparams = None):
		self.okmethod = okmethod
		self.cancelmethod = cancelmethod
		self.okparams = okparams
		self.cancelparams = cancelparams
		glade_path="glade/pytrainer.glade"
		self.path = data_path+glade_path
		root = "warning"
		domain = None
		SimpleGladeApp.__init__(self, self.path, root, domain)
		if okmethod == None:
			self.cancelbutton1.hide()

	def set_text(self, msg):
		self.warningText.set_text(msg)
	
	def on_accept_clicked(self,widget):
		if self.okparams != None:
			num = len(self.okparams)
			if num==0:
				self.okmethod()
			if num==1:
				self.okmethod(self.okparams[0])
			if num==2:
				self.okmethod(self.okparams[0],self.okparams[1])
		self.close_window()
	
	def on_cancel_clicked(self,widget):
		self.warning.hide()
		if self.cancelparams != None:
			num = len(self.cancelparams)
			if num==0:
				self.cancelmethod()
			if num==1:
				self.cancelmethod(self.cancelparams[0])
			if num==2:
				self.cancelmethod(self.cancelparams[0], self.cancelparams[1])
		self.close_window()

	def close_window(self):
		self.warning.hide()
		self.warning = None
		self.quit()
		
