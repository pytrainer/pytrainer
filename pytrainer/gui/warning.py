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

from pytrainer.gui.dialogs import warning_dialog
import gtk
import logging

class Warning(object):
    def __init__(self, data_path = None, okmethod = None, okparams = None, cancelmethod = None, cancelparams = None):
        logging.warning("Deprecated Warning class called")
        self.okmethod = okmethod
        self.cancelmethod = cancelmethod
        self.okparams = okparams
        self.cancelparams = cancelparams
        self.text = ""
        self.title = "Warning"

    def set_title(self, title):
        self.title = title

    def set_text(self, msg):
        self.text = msg

    def on_accept_clicked(self):
        if self.okparams != None:
            num = len(self.okparams)
            if num==0:
                self.okmethod()
            if num==1:
                self.okmethod(self.okparams[0])
            if num==2:
                self.okmethod(self.okparams[0],self.okparams[1])

    def on_cancel_clicked(self):
        if self.cancelparams != None:
            num = len(self.cancelparams)
            if num==0:
                self.cancelmethod()
            if num==1:
                self.cancelmethod(self.cancelparams[0])
            if num==2:
                self.cancelmethod(self.cancelparams[0], self.cancelparams[1])

    def run(self):
        if self.okmethod:
            response = warning_dialog(text=self.text, title=self.title, cancel=True)
        else:
            response = warning_dialog(text=self.text, title=self.title, cancel=False)
        if response == gtk.RESPONSE_OK:
            self.on_accept_clicked()
        elif response == gtk.RESPONSE_CANCEL:
            self.on_cancel_clicked()
