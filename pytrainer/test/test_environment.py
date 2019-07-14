# -*- coding: utf-8 -*-

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

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from pytrainer.environment import Environment

TEST_DIR_NAME = "/test/.pytrainer_test"
DATA_DIR_NAME = "/test/datadir"

class Test(unittest.TestCase):

    def setUp(self):
        self.environment = Environment()
        # Environment is a singleton, make sure to destroy it between tests
        del(Environment.self)
        self.environment = Environment(TEST_DIR_NAME, DATA_DIR_NAME)

    def tearDown(self):
        del(Environment.self)

    def test_get_conf_dir(self):
        self.assertEqual(TEST_DIR_NAME, self.environment.conf_dir)

    def test_get_data_path(self):
        self.assertEqual(DATA_DIR_NAME, self.environment.data_path)

    def test_environment_singleton(self):
        self.environment = Environment()
        self.assertEqual(TEST_DIR_NAME, self.environment.conf_dir)
        self.assertEqual(DATA_DIR_NAME, self.environment.data_path)
        
    def test_get_conf_file(self):
        self.assertEqual(TEST_DIR_NAME + "/conf.xml", self.environment.conf_file)

    def test_get_log_file(self):
        self.assertEqual(TEST_DIR_NAME + "/log.out", self.environment.log_file)

    def test_get_temp_dir(self):
        self.assertEqual(TEST_DIR_NAME + "/tmp", self.environment.temp_dir)

    def test_get_gpx_dir(self):
        self.assertEqual(TEST_DIR_NAME + "/gpx", self.environment.gpx_dir)

    def test_get_extension_dir(self):
        self.assertEqual(TEST_DIR_NAME + "/extensions", self.environment.extension_dir)

    def test_get_plugin_dir(self):
        self.assertEqual(TEST_DIR_NAME + "/plugins", self.environment.plugin_dir)
        

if __name__ == "__main__":
    unittest.main()
