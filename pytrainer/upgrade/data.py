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

import logging
from lxml import etree
import pytrainer
from pytrainer.upgrade.context import UpgradeContext
from pytrainer.upgrade.migratedb import MigratableDb

MIGRATE_REPOSITORY_PATH = "pytrainer/upgrade"

def initialize_data(ddbb, conf_dir):
    """Initializes the installation's data."""
    db_url = ddbb.get_connection_url()
    migratable_db = MigratableDb(MIGRATE_REPOSITORY_PATH, db_url)
    InstalledData(migratable_db, ddbb, LegacyVersionProvider(conf_dir)).update_to_current()
        
class InstalledData(object):
    
    """Encapsulates an installation's existing data and provides means to
    check version state and upgrade."""
    
    def __init__(self, migratable_db, ddbb, legacy_version_provider):
        self._migratable_db = migratable_db
        self._ddbb = ddbb
        self._legacy_version_provider = legacy_version_provider
        
    def update_to_current(self):
        """Check the current state of the installation's data and update them
        if necessary so they are compatible with the latest version.
    
        The update steps depend on the state of the installation's data. The
        possible states and the update steps from those states are:
    
        1. Current (data is up to date):
            - do nothing
        2. Fresh (new installation):
            - initialise empty db
            - initialise db version metadata
        3. Stale: (data requires upgrading):
            - run upgrade scripts
        4. Legacy (data requires upgrading but is missing version metadata):
            - initialise db version metadata
            - run upgrade scripts
        
        """
        data_state = self.get_state()
        logging.info("Initializing data. Data state is: '%s'.", data_state)
        data_state.update_to_current(self)
        
    def get_state(self):
        version = self.get_version()
        available_version= self.get_available_version()
        if self.is_versioned():
            if version == available_version:
                return DataState.CURRENT
            elif version > available_version:
                raise ValueError("Current version ({0}) is greater than available version ({1}).".format(version, available_version))
            else:
                return DataState.STALE
        else:
            if version == None:
                return DataState.FRESH
            else:
                return DataState.LEGACY
    
    def get_version(self):
        """Get the version number of an installation's data.
        
        If the data is empty then None is returned."""
        if self.is_versioned():
            return self._migratable_db.get_version()
        else:
            # Calculate data version in older version that does not use the
            # current data versioning scheme.
            legacy_version = self._legacy_version_provider.get_legacy_version()
            if legacy_version is not None:
                legacy_version = int(legacy_version)
                if legacy_version <= 6:
                    return legacy_version
                elif legacy_version == 7:
                    return 9
                elif legacy_version == 8:
                    return 10
                elif legacy_version == 9:
                    return 10
            return None
        
    def get_available_version(self):
        return self._migratable_db.get_upgrade_version()
        
    def is_versioned(self):
        """ Check if the version metadata has been initiaized."""
        return self._migratable_db.is_versioned()
    
    def initialize_version(self, initial_version):
        """Initialize the version metadata."""
        logging.info("Initializing version metadata to version: '%s'.", initial_version)
        self._migratable_db.version(initial_version)
        
    def initialize(self):
        logging.info("Initializing new database.")
        self._ddbb.create_tables()
        
    def upgrade(self):
        logging.info("Upgrading data from version '%s' to version '%s'.", self.get_version(), self.get_available_version())
        pytrainer.upgrade.context.UPGRADE_CONTEXT = UpgradeContext(self._conf_dir)
        self._migratable_db.upgrade()
        
class DataState(object):
    
    """The state of an installation's data.
    
    The state knows how to update the data to the "current" state."""

    def __init__(self, name, update_function):
        self.name = name
        self._update_function = update_function
        
    def __str__(self):
        return self.name
        
    def update_to_current(self, installed_data):
        """Update the installed data so it is compatible with the current
        version."""
        self._update_function(installed_data)

def _update_fresh(data):
    data.initialize()
    data.initialize_version(data.get_available_version())

def _update_stale(data):
    data.upgrade()

def _update_legacy(data):
    data.initialize_version(data.get_version())
    data.upgrade()

DataState.CURRENT = DataState("CURRENT", lambda data: None)
DataState.FRESH = DataState("FRESH", _update_fresh)
DataState.STALE = DataState("STALE", _update_stale)
DataState.LEGACY = DataState("LEGACY", _update_legacy)

class LegacyVersionProvider(object):
    
    """Provides the DB version number for data not using the current data
    versioning scheme."""
    
    def __init__(self, conf_dir):
        self._conf_dir = conf_dir
        
    def get_legacy_version(self):
        # In versions 1.7 and 1.8 the database version was stored as a property
        # in the config file. Versions earlier than 1.7 are not supported for
        # upgrades.
        config_file = self._conf_dir + "/conf.xml"
        parser = etree.XMLParser(encoding="UTF8", recover=True)
        xml_tree = etree.parse(config_file, parser=parser)
        config_element = xml_tree.getroot()
        return config_element.get("DB_version")
