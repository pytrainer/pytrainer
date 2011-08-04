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

import unittest
from mock import Mock
from pytrainer.upgrade.data import InstalledData, DataState

class InstalledDataTest(unittest.TestCase):
    
    def setUp(self):
        self._mock_migratable_db = Mock()
        self._mock_ddbb = Mock()
        self._mock_version_provider = Mock()
        self._installed_data = InstalledData(self._mock_migratable_db, self._mock_ddbb, self._mock_version_provider)
        
    def test_get_version_should_return_migrate_version_when_available(self):
        self._mock_migratable_db.get_version.return_value = 1
        self.assertEquals(1, self._installed_data.get_version())
        
    def test_get_version_should_return_legacy_version_when_available(self):
        self._mock_migratable_db.is_versioned.return_value = False
        self._mock_version_provider.get_legacy_version.return_value = 2
        self.assertEquals(2, self._installed_data.get_version())
        
    def test_get_version_should_return_none_when_no_existing_version(self):
        self._mock_migratable_db.is_versioned.return_value = False
        self._mock_version_provider.get_legacy_version.return_value = None
        self.assertEquals(None, self._installed_data.get_version())
        
    def test_get_state_should_return_current_when_data_version_equals_repository_version(self):
        self._mock_migratable_db.get_version.return_value = 1
        self._mock_migratable_db.get_upgrade_version.return_value = 1
        self.assertEquals(DataState.CURRENT, self._installed_data.get_state())

    def test_get_state_should_return_fresh_when_data_version_unavailable(self):
        self._mock_migratable_db.is_versioned.return_value = False
        self._mock_version_provider.get_legacy_version.return_value = None
        self.assertEquals(DataState.FRESH, self._installed_data.get_state())

    def test_get_state_should_return_stale_when_data_version_less_than_repository_version(self):
        self._mock_migratable_db.get_version.return_value = 1
        self._mock_migratable_db.get_upgrade_version.return_value = 2
        self.assertEquals(DataState.STALE, self._installed_data.get_state())

    def test_get_state_should_return_legacy_when_data_version_is_legacy(self):
        self._mock_migratable_db.is_versioned.return_value = False
        self._mock_version_provider.get_legacy_version.return_value = 1
        self.assertEquals(DataState.LEGACY, self._installed_data.get_state())

    def test_get_state_should_raise_error_when_version_too_large(self):
        self._mock_migratable_db.is_versioned.return_value = True
        self._mock_migratable_db.get_version.return_value = 2
        self._mock_migratable_db.get_upgrade_version.return_value = 1
        try:
            self._installed_data.get_state()
        except ValueError:
            pass
        else:
            self.fail()
