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
import logging

class Environment(object):
    
    """Describes the location of the program's configuration directories and files."""
    
    def __init__(self, platform, conf_dir):
        """Initialise an environment.
        
        Arguments:
        platform -- the current system platform.
        conf_dir -- the directory where program configuration should be stored. If None, then the default for the platform is used.
        
        """
        self.conf_dir = conf_dir if conf_dir is not None else platform.get_default_conf_dir()
        logging.info("Initializing environment. Conf dir is: '{0}'.".format(self.conf_dir))
        self.conf_file = self.conf_dir + "/conf.xml"
        self.log_file = self.conf_dir + "/log.out"
        self.temp_dir = self.conf_dir + "/tmp"
        self.gpx_dir = self.conf_dir + "/gpx"
        self.extension_dir = self.conf_dir + "/extensions"
        self.plugin_dir = self.conf_dir + "/plugins"
            
    def clear_temp_dir(self):
        """Remove all files from the tmp directory."""
        logging.debug("clearing tmp directory %s" % self.temp_dir)
        if not os.path.isdir(self.temp_dir):
            return
        else:
            files = os.listdir(self.temp_dir)
            for name in files:
                fullname = (os.path.join(self.temp_dir, name))
                if os.path.isfile(fullname):
                    os.remove(os.path.join(self.temp_dir, name))
            
    def create_directories(self):
        """Create all required directories if they do not already exist."""
        self._create_dir(self.conf_dir)
        self._create_dir(self.temp_dir)
        self._create_dir(self.extension_dir)
        self._create_dir(self.plugin_dir)
        self._create_dir(self.gpx_dir)
            
    def _create_dir(self, dir_name):
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)
