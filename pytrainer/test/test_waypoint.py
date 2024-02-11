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
from unittest.mock import Mock

from pytrainer.lib.ddbb import DDBB
from pytrainer.waypoint import WaypointService

class WaypointTest(unittest.TestCase):

    def setUp(self):
        self.ddbb = DDBB()
        main = Mock()
        main.ddbb = self.ddbb
        main.ddbb.connect()
        main.ddbb.create_tables(add_default=False)
        self.waypoint = WaypointService(parent=main)

    def tearDown(self):
        self.waypoint = None
        self.ddbb.disconnect()
        self.ddbb.drop_tables()

    def test_waypoint_add_and_get(self):
        data = (30.0, 20.0, None, u'Comment', None, u'Test', u'sym')
        dbid = self.waypoint.addWaypoint(lat=data[0], lon=data[1],
                                         name=data[5], comment=data[3],
                                         sym=data[6])
        data2 = self.waypoint.getwaypointInfo(dbid)
        self.assertEqual(data, data2[0])

    def test_waypoint_update(self):
        data = (30.0, 20.0, None, u'Comment', None, u'Test', u'sym')
        dbid = self.waypoint.addWaypoint(lat=50, lon=60, name='Test2',
                                         comment='Comment 2', sym='sym2')
        self.waypoint.updateWaypoint(dbid, data[0], data[1], data[5], data[3],
                                     data[6])
        data2 = self.waypoint.getwaypointInfo(dbid)
        self.assertEqual(data, data2[0])

    def test_waypoint_get_all(self):
        data = (30.0, 20.0, None, u'Comment', None, u'Test', u'sym')
        dbid = self.waypoint.addWaypoint(lat=data[0], lon=data[1],
                                         name=data[5], comment=data[3],
                                         sym=data[6])
        dbid = self.waypoint.addWaypoint(lat=50, lon=60, name='Test2',
                                         comment='Comment 2', sym='sym2')
        self.assertEqual(len(self.waypoint.getAllWaypoints()), 2)

    def test_waypoint_remove(self):
        data = (30.0, 20.0, None, u'Comment', None, u'Test', u'sym')
        dbid = self.waypoint.addWaypoint(lat=data[0], lon=data[1],
                                         name=data[5], comment=data[3],
                                         sym=data[6])
        dbid = self.waypoint.addWaypoint(lat=50, lon=60, name='Test2',
                                         comment='Comment 2', sym='sym2')
        self.waypoint.removeWaypoint(dbid)
        self.assertEqual(len(self.waypoint.getAllWaypoints()), 1)
