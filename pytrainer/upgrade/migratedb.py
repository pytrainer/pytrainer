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

from migrate.versioning.api import db_version, upgrade, version, version_control
from migrate.versioning.exceptions import DatabaseNotControlledError

class MigratableDb(object):
    """Object bridge for sqlalchemy-migrate API functions."""
    
    def __init__(self, repository_path, db_url):
        self._repository_path = repository_path
        self._db_url = db_url
        
    def is_versioned(self):
        """ Check if the DB has been initiaized with version metadata."""
        try:
            self.get_version()
        except DatabaseNotControlledError:
            return False
        return True
        
    def get_version(self):
        """Get the current version of the versioned DB.
        
        Raises DatabaseNotControlledError if the DB is not initialized."""
        return db_version(self._db_url, self._repository_path)
    
    def get_upgrade_version(self):
        """Get the latest version available in upgrade repository."""
        return version(self._repository_path)
    
    def version(self, initial_version):
        """Initialize the database with migrate metadata.
        
        Raises DatabaseAlreadyControlledError if the DB is already initialized."""
        version_control(self._db_url, self._repository_path, initial_version)

    def upgrade(self):
        """Run all available upgrade scripts for the repository."""
        upgrade(self._db_url, self._repository_path)
