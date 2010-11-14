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

import pytrainer.platform
from pytrainer.environment import Environment

TEST_DIR_NAME = "/test/.pytrainer_test"

PLATFORM = pytrainer.platform.get_platform()

class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_conf_dir(self):
        environment = Environment(PLATFORM, TEST_DIR_NAME)
        self.assertEquals(TEST_DIR_NAME, environment.conf_dir)
        
    def test_get_conf_dir_default(self):
        test_platform = Mock(spec=pytrainer.platform.get_platform())
        test_platform.get_default_conf_dir.return_value = "/test/.pytrainer_test"
        environment = Environment(test_platform, None)
        self.assertEquals("/test/.pytrainer_test", environment.conf_dir)

    def test_get_conf_file(self):
        environment = Environment(PLATFORM, TEST_DIR_NAME)
        self.assertEquals(TEST_DIR_NAME + "/conf.xml", environment.conf_file)

    def test_get_log_file(self):
        environment = Environment(PLATFORM, TEST_DIR_NAME)
        self.assertEquals(TEST_DIR_NAME + "/log.out", environment.log_file)

    def test_get_temp_dir(self):
        environment = Environment(PLATFORM, TEST_DIR_NAME)
        self.assertEquals(TEST_DIR_NAME + "/tmp", environment.temp_dir)

    def test_get_gpx_dir(self):
        environment = Environment(PLATFORM, TEST_DIR_NAME)
        self.assertEquals(TEST_DIR_NAME + "/gpx", environment.gpx_dir)

    def test_get_extension_dir(self):
        environment = Environment(PLATFORM, TEST_DIR_NAME)
        self.assertEquals(TEST_DIR_NAME + "/extensions", environment.extension_dir)

    def test_get_plugin_dir(self):
        environment = Environment(PLATFORM, TEST_DIR_NAME)
        self.assertEquals(TEST_DIR_NAME + "/plugins", environment.plugin_dir)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()