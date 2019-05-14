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
from datetime import date
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from pytrainer.lib.uc import *

class UCUtilTest(unittest.TestCase):

    def test_uc_pace2float(self):
        self.assertEqual(4.1, pace2float('4:06'))

    def test_uc_float2pace(self):
        self.assertEqual('4:06', float2pace(4.1))

class UCTest(unittest.TestCase):

    def setUp(self):
        self.uc = UC()
        self.uc.set_us(False)

    def tearDown(self):
        self.uc = None

    def test_uc_units(self):
        self.assertEqual(self.uc.unit_distance, "km")
        self.assertEqual(self.uc.unit_speed, "km/h")
        self.assertEqual(self.uc.unit_pace, "min/km")
        self.assertEqual(self.uc.unit_height, "m")
        self.assertEqual(self.uc.unit_weight, "kg")
        self.uc.set_us(True)
        self.assertEqual(self.uc.unit_distance, "mi")
        self.assertEqual(self.uc.unit_speed, "mph")
        self.assertEqual(self.uc.unit_pace, "min/mi")
        self.assertEqual(self.uc.unit_height, "ft")
        self.assertEqual(self.uc.unit_weight, "lb")

    def test_uc_conversions(self):
        self.assertEqual(self.uc.distance(10), 10)
        self.assertEqual(self.uc.speed(10), 10)
        self.assertEqual(self.uc.pace(10), 10)
        self.assertEqual(self.uc.height(10), 10)
        self.assertEqual(self.uc.weight(10), 10)
        self.uc.set_us(True)
        self.assertEqual(self.uc.distance(10), 6.21371192)
        self.assertEqual(self.uc.speed(10), 6.21371192)
        self.assertEqual(self.uc.pace(10), 16.09344)
        self.assertEqual(self.uc.height(10), 32.808399)
        self.assertEqual(self.uc.weight(10), 22.046239999999997)
