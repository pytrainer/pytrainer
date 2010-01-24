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

class WindowCalendar(SimpleGladeApp):
	def __init__(self, data_path = None, parent = None, date = None):
		self.parent = parent
		glade_path="glade/calendar.glade"
		root = "calendardialog"
		domain = None
		SimpleGladeApp.__init__(self, data_path+glade_path, root, domain)
		if date is not None:
			try:
				year, month, day = date.split("-")
				self.calendar.select_month( int(month)-1, int(year) )
				self.calendar.select_day( int(day) )
			except:	
				pass
		
	def on_accept_clicked(self,widget):
		date = self.calendar.get_date()	
		date = "%0.4d-%0.2d-%0.2d" %(date[0],date[1]+1,date[2])
		self.parent.setDate(date)
		self.close_window()

	def on_cancel_clicked(self,widget):
		self.close_window()

	def close_window(self):
		self.calendardialog.hide()
		self.calendardialog = None
		self.quit()
