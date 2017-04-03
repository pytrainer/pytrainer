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
import datetime
from dateutil.tz import tzutc, tzlocal
from pytrainer.lib.date import second2time, time2second, time2string, unixtime2date, getNameMonth, getDateTime

class DateFunctionTest(unittest.TestCase):

    def test_second2time(self):
        tmp = second2time(3912)
        self.assertEqual((1, 5, 12), tmp)

    def test_time2second(self):
        tmp = time2second((1, 5, 12))
        self.assertEqual(3912, tmp)

    def test_time2string(self):
        tmp = time2string((2015, 11, 24))
        self.assertEqual('2015-11-24', tmp)

    def test_getNameMonth(self):
        monthname, daysinmonth = getNameMonth(datetime.date(2015, 11, 24))
        self.assertEqual('November', monthname)
        self.assertEqual(30, daysinmonth)

    def test_unixtime2date(self):
        tmp = unixtime2date(1448378940)
        self.assertEqual('2015-11-24', tmp)

    def test_getDateTime(self):
        utctime, localtime = getDateTime('Tue Nov 24 17:29:05 UTC 2015')
        self.assertEqual(datetime.datetime(2015, 11, 24, 17, 29, 5, tzinfo=tzutc()), utctime)
        self.assertEqual(datetime.datetime(2015, 11, 24, 19, 29, 5, tzinfo=tzlocal()), localtime)
