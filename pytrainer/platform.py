# -*- coding: iso-8859-1 -*-

#Copyright (C) Nathan Jones ncjones@users.sourceforge.net
#modified by dgranda on behalf of Debian bug #587997 (trac ticket #120)

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
import subprocess
import datetime
import logging
    
def get_platform():
    if os.name == "posix":
        return _Linux() #although not true, not changing original return name to avoid side effects
    elif os.name == "nt":
        return _Windows()
    else:
        logging.critical("Unsupported os.name: %s.", os.name)
        sys.exit(1)
        
class _Platform(object):
    
    def get_default_conf_dir(self):
        """Get the path to the default configuration directory for the platform."""
        return self._home_dir + "/" + self._conf_dir_name

    def get_default_data_path(self):
        """Get the path to the default data directory for the platform."""
        return self._data_path

    def get_first_day_of_week(self):
        """Determine the first day of the week for the system locale.
        If the first day of the week cannot be determined then Sunday is assumed.
        Returns (int): a day of the week; 0: Sunday, 1: Monday, 6: Saturday.
"""
        return self._first_day_of_week

class _Linux(_Platform):
    
    def __init__(self):
        self._home_dir = os.environ['HOME']
        self._conf_dir_name = ".pytrainer"
        self._data_path = "/usr/share/pytrainer/"
        try:
            results = subprocess.check_output(("locale", "first_weekday", "week-1stday"),
                                              universal_newlines=True).splitlines()
            day_delta = datetime.timedelta(days=int(results[0]) - 1)
            base_date = datetime.datetime.strptime(results[1], "%Y%m%d")
            first_day = base_date + day_delta
            self._first_day_of_week = int(first_day.strftime("%w"))
        except subprocess.CalledProcessError:
            self._first_day_of_week = 0

class _Windows(_Platform):
    
    def __init__(self):
        self._home_dir = os.environ['USERPROFILE']
        self._conf_dir_name = "pytrainer"
        self._data_path = os.getcwd() + os.sep
        self._first_day_of_week = 0
