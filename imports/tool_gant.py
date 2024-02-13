# -*- coding: utf-8 -*-

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
import os, sys, subprocess
from lxml import etree

class gant():
    def __init__(self, parent = None, data_path = None):
        self.parent = parent
        self.pytrainer_main = parent.parent
        self.tmpdir = self.pytrainer_main.profile.tmpdir
        self.main_data_path = data_path
        self.data_path = os.path.dirname(__file__)

    def getName(self):
        return _("Gant")

    def getVersion(self):
        process = subprocess.Popen(['which', 'gant'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0: # Found gant in path
            path = stdout[:-1] # remove trailing newline
            return path
        else:
            return None
        return None

    def getSourceLocation(self):
        return "http://cgit.get-open.com/cgit.cgi/gant/"

    def deviceExists(self):
        return True

    def isPresent(self):
        return self.getVersion() is not None
