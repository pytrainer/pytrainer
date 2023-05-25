# -*- coding: utf-8 -*-

#Copyright (C) Arto Jantunen <viiru@iki.fi>

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
    from unittest import mock
except ImportError:
    import mock

try:
    import MySQLdb
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

from pytrainer.lib.ddbb import DDBB


class DDBBTest(unittest.TestCase):

    def setUp(self):
        # DDBB is a singleton, make sure to destroy it between tests
        self.ddbb = DDBB()
        del(DDBB.self)

    def tearDown(self):
        del(DDBB.self)

    @mock.patch.dict('os.environ', {}, clear=True)
    def test_none_url(self):
        self.ddbb = DDBB()
        self.assertEqual(self.ddbb.url, 'sqlite://')

    def test_basic_url(self):
        self.ddbb = DDBB(url='sqlite:///test_url')
        self.assertEqual(self.ddbb.url, 'sqlite:///test_url')

    @unittest.skipUnless(MYSQL_AVAILABLE, 'MySQLdb library not available')
    def test_mysql_url(self):
        self.ddbb = DDBB(url='mysql://pytrainer@localhost/pytrainer')
        self.assertEqual(self.ddbb.url, 'mysql://pytrainer@localhost/pytrainer?charset=utf8')

    @mock.patch.dict('os.environ', {'PYTRAINER_ALCHEMYURL': 'sqlite:///envtest'})
    def test_env_url(self):
        self.ddbb = DDBB()
        self.assertEqual(self.ddbb.url, 'sqlite:///envtest')

    @mock.patch.dict('os.environ', {'PYTRAINER_ALCHEMYURL': 'mysql://pytrainer@localhost/pytrainer'})
    @unittest.skipUnless(MYSQL_AVAILABLE, 'MySQLdb library not available')
    def test_env_mysql_url(self):
        self.ddbb = DDBB()
        self.assertEqual(self.ddbb.url, 'mysql://pytrainer@localhost/pytrainer?charset=utf8')

    def test_singleton(self):
        self.ddbb = DDBB(url='sqlite:///test_url')
        self.assertEqual(self.ddbb.url, 'sqlite:///test_url')
        self.ddbb = DDBB()
        self.assertEqual(self.ddbb.url, 'sqlite:///test_url')
