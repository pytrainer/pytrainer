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

import logging
from pytrainer.gui.dialogs import calendar_dialog

class WindowCalendar(object):
    def __init__(self, data_path = None, parent = None, date = None):
        logging.warning("Deprecated WindowCalendar class called")
        self.parent = parent
        self.date = date

    def run(self):
        date = calendar_dialog(date=self.date)
        if date:
            self.parent.setDate(date)
