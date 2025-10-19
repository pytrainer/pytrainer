# -*- coding: utf-8 -*-

#Copyright (C) Arto Jantunen <viiru@iki.fi>

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

from gi.repository import Gtk
from pytrainer.environment import Environment
from pytrainer.gui.dialogs import calendar_dialog

env = Environment()

@Gtk.Template(filename=env.glade_dir + "/date-entry.ui")
class DateEntry(Gtk.Entry):
    __gtype_name__ = "DateEntry"

    def __init__(self):
        super(DateEntry, self).__init__()

    @Gtk.Template.Callback()
    def on_calendar_clicked(self, widget, icon_pos, event):
        date = calendar_dialog(date=self.get_text())
        if date:
            self.set_text(date)
