# -*- coding: iso-8859-1 -*-

#Copyright (C) Nathan Jones ncjones@users.sourceforge.net

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
import sys
    
def get_platform():
    if sys.platform == "linux2":
        return _Linux()
    elif sys.platform == "win32":
        return _Windows()
    else:
        print "Unsupported sys.platform: %s." % sys.platform
        sys.exit(1)
        
class _Platform(object):
    
    def get_default_conf_dir(self):
        """Get the path to the default configuration directory for the platform."""
        return self._home_dir + "/" + self._conf_dir_name

class _Linux(_Platform):
    
    def __init__(self):
        self._home_dir = os.environ['HOME']
        self._conf_dir_name = ".pytrainer"

class _Windows(_Platform):
    
    def __init__(self):
        self._home_dir = os.environ['USERPROFILE']
        self._conf_dir_name = "pytrainer"
