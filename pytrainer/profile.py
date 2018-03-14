# -*- coding: iso-8859-1 -*-

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

import os, stat
import logging
from io import BytesIO
from gettext import gettext as _

from lxml import etree
from environment import Environment
from pytrainer.lib.singleton import Singleton
from lib.uc import UC

class Profile(Singleton):
    def __init__(self):
        logging.debug(">>")
        # The first two variables are singletons themselves, profile_options
        # doesn't change, only xml_tree needs to be protected by has_attr.
        self.environment = Environment()
        self.uc = UC()
        #Profile Options and Defaults
        self.profile_options = {
            "prf_name":"default",
            "prf_gender":"",
            "prf_weight":"",
            "prf_height":"",
            "prf_age":"",
            "prf_ddbb":"sqlite",
            "prf_ddbbhost":"",
            "prf_ddbbname":"",
            "prf_ddbbuser":"",
            "prf_ddbbpass":"",
            "version":"0.0",
            "prf_us_system":"False",
            "prf_hrzones_karvonen":"False",
            "prf_maxhr":"",
            "prf_minhr":"",
            "auto_launch_file_selection":"False",
            "import_default_tab":"0",
            "default_viewer":"0",
            "window_size":"800, 640",
            "activitypool_size": "10",
            "prf_startscreen":"current_day",
            }

        if not hasattr(self, 'xml_tree'):
            self.xml_tree = None
            #Parse pytrainer configuration file
            self.refreshConfiguration()

        logging.debug("<<")

    @property
    def data_path(self):
        return self.environment.data_path

    @property
    def tmpdir(self):
        return self.environment.temp_dir

    @property
    def confdir(self):
        return self.environment.conf_dir

    @property
    def config_file(self):
        return self.environment.conf_file

    @property
    def gpxdir(self):
        return self.environment.gpx_dir

    @property
    def extensiondir(self):
        return self.environment.extension_dir

    @property
    def plugindir(self):
        return self.environment.plugin_dir

    @property
    def sqlalchemy_url(self):
        ddbb_type = self.getValue("pytraining","prf_ddbb")
        ddbb_host = self.getValue("pytraining","prf_ddbbhost")
        ddbb = self.getValue("pytraining","prf_ddbbname")
        ddbb_user = self.getValue("pytraining","prf_ddbbuser")
        ddbb_pass = self.getValue("pytraining","prf_ddbbpass")
        if ddbb_type == "sqlite":
            return "sqlite:///%s/pytrainer.ddbb" % self.confdir
        else:
            return "{type}://{user}:{passwd}@{host}/{db}".format(type=ddbb_type,
                                                                 user=ddbb_user,
                                                                 passwd=ddbb_pass,
                                                                 host=ddbb_host,
                                                                 db=ddbb)

    def refreshConfiguration(self):
        logging.debug(">>")
        self.configuration = self._parse_config_file(self.config_file)
        logging.debug("Configuration retrieved: %s", str(self.configuration))
        self.uc.set_us(self.prf_us_system)
        self._setZones()
        logging.debug("<<")

    def _setZones(self):
        #maxhr = self.getValue("pytraining","prf_maxhr")
        #resthr = self.getValue("pytraining","prf_minhr")
        try:
            maxhr = int(self.getValue("pytraining","prf_maxhr"))
        except Exception as e:
            logging.error("Failed when retrieving Max Heartrate value: %s" %e)
            logging.info("Setting Max Heartrate to default value: 190")
            maxhr = 190
        try:
            resthr = int(self.getValue("pytraining","prf_minhr"))
        except Exception as e:
            logging.error("Failed when retrieving Min Heartrate value: %s" %e)
            logging.info("Setting Min Heartrate to default value: 65")
            resthr = 65
        self.maxhr = maxhr
        self.rethr = resthr

        if self.getValue("pytraining","prf_hrzones_karvonen")=="True":
            #karvonen method
            targethr1 = ((maxhr - resthr) * 0.50) + resthr
            targethr2 = ((maxhr - resthr) * 0.60) + resthr
            targethr3 = ((maxhr - resthr) * 0.70) + resthr
            targethr4 = ((maxhr - resthr) * 0.80) + resthr
            targethr5 = ((maxhr - resthr) * 0.90) + resthr
            targethr6 = maxhr
        else:
            #not karvonen method
            targethr1 = maxhr * 0.50
            targethr2 = maxhr * 0.60
            targethr3 = maxhr * 0.70
            targethr4 = maxhr * 0.80
            targethr5 = maxhr * 0.90
            targethr6 = maxhr

        self.zone1 = (targethr1,targethr2,"#ffff99",_("Moderate activity"))
        self.zone2 = (targethr2,targethr3,"#ffcc00",_("Weight Control"))
        self.zone3 = (targethr3,targethr4,"#ff9900",_("Aerobic"))
        self.zone4 = (targethr4,targethr5,"#ff6600",_("Anaerobic"))
        self.zone5 = (targethr5,targethr6,"#ff0000",_("VO2 MAX"))
        
    def getMaxHR(self):
        return self.maxhr
        
    def getRestHR(self):
        return self.resthr

    def getZones(self):
        return self.zone5,self.zone4,self.zone3,self.zone2,self.zone1

    def _parse_config_file(self, config_file):
        '''
        Parse the xml configuration file and convert to a dict

        returns: dict with option as key
        '''
        if config_file is None:
            logging.error("Configuration file value not set")
            logging.error("Fatal error, exiting")
            exit(-3)
        elif not os.path.isfile(config_file): #File not found
            logging.error("Configuration '%s' file does not exist" % config_file)
            logging.info("No profile found. Creating default one")
            self.setProfile(self.profile_options)
        elif os.stat(config_file)[stat.ST_SIZE] == 0: #File is empty
            logging.error("Configuration '%s' file is empty" % config_file)
            logging.info("Creating default profile")
            self.setProfile(self.profile_options)
        else:
            logging.debug("Attempting to parse content from %s", config_file)
            parser = etree.XMLParser(encoding='UTF8', recover=True)
            try:
                self.xml_tree = etree.parse(config_file, parser=parser)
            except Exception as e:
                logging.error("Error %s while parsing file %s. Exiting", e, config_file)
                exit(-3)
        #Have a populated xml tree, get pytraining node (root) and convert it to a dict
        pytraining_tag = self.xml_tree.getroot()
        config = {}
        config_needs_update = False
        for key, default in self.profile_options.items():
            value = pytraining_tag.get(key)
            #If property is not found, set it to the default
            if value is None:
                config_needs_update = True
                value = default
            config[key] = value
        #Added a property, so update config
        if config_needs_update:
            self.setProfile(config)
        #Set shorthand var for units of measurement
        self.prf_us_system = True if config["prf_us_system"] == "True" else False
        return config

    def getIntValue(self, tag, variable, default=0):
        ''' Function to return conf value as int
            returns
            -- default if cannot convert to int
            -- None if variable not found
        '''
        result = self.getValue(tag, variable)
        if result is None:
            return None
        try:
            result = int(result)
        except Exception as e:
            logging.debug(str(e))
            result = default
        return result

    def getValue(self, tag, variable):
        if tag != "pytraining":
            logging.critical("ERROR - pytraining is the only profile tag supported")
            return None
        elif not self.configuration.has_key(variable):
            return None
        return self.configuration[variable]

    def setValue(self, tag, variable, value, delay_write=False):
        logging.debug(">>")
        if tag != "pytraining":
            logging.error("ERROR: pytraining is the only profile tag supported")
        logging.debug("Setting %s to %s" % (variable, value))
        if self.xml_tree is None:
            #new config file....
            self.xml_tree = etree.parse(BytesIO(b'''<?xml version='1.0' encoding='UTF-8'?><pytraining />'''))
        self.xml_tree.getroot().set(variable, value.decode('utf-8'))
        if not delay_write:
            self.saveProfile()
        logging.debug("<<")

    def setProfile(self,list_options):
        logging.debug(">>")
        for option, value in list_options.items():
            logging.debug("Adding "+option+"|"+value)
            self.setValue("pytraining",option,value,delay_write=True)
        self.uc.set_us(list_options['prf_us_system'])
        logging.debug("<<")

    def saveProfile(self):
        logging.debug("Writting configuration...")
        self.xml_tree.write(self.config_file, xml_declaration=True,
                            encoding='UTF-8')
