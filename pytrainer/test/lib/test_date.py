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
from unittest.mock import Mock
from dateutil.tz import tzutc, tzlocal
from pytrainer.lib.date import second2time, time2second, time2string, unixtime2date, getNameMonth, getDateTime
from pytrainer.lib.date import Date, DateRange

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


class DateTest(unittest.TestCase):

    def test_getDate_should_return_valid_date_if_day_is_too_large(self):
        mock_calendar = Mock()
        attrs = {'get_date.return_value': (2019, 1, 31)} # 2019-02-31
        mock_calendar.configure_mock(**attrs)
        self.assertEqual(datetime.date(2019,2,28),
                         Date(mock_calendar).getDate())

    def test_getDate_should_raise_ValueError_if_day_is_before_first(self):
        mock_calendar = Mock()
        attrs = {'get_date.return_value': (2019, 1, 0)} # 2019-02-00
        mock_calendar.configure_mock(**attrs)
        with self.assertRaises(ValueError):
            Date(mock_calendar).getDate()

    def test_getDate_should_return_valid_date_if_date_is_valid(self):
        mock_calendar = Mock()
        start_date = datetime.date(2019, 1, 1)
        # list of every day in 2019 (non-leap year) and 2020 (leap year)
        date_list = [start_date + datetime.timedelta(days=x) for x in range(0, 731)]
        end_date = datetime.date(2019, 12, 31)
        # test every day in the list
        for date in date_list:
           # python3 way : with self.subTest(date=date):
            try :
                mock_calendar = Mock()
                # act as gtk calendar where months are numbered from 0 to 11
                attrs = {'get_date.return_value': (date.year, date.month - 1, date.day)}
                mock_calendar.configure_mock(**attrs)
                self.assertEqual((datetime.date(date.year, date.month, date.day)),
                                  Date(mock_calendar).getDate())
            except :
                self.fail("Failed with date %s-%s-%s" % (date.year, date.month, date.day))

class DateRangeTest(unittest.TestCase):

    def test_constructor_should_accept_end_date_same_as_start_date(self):
        DateRange(datetime.date(2011, 9, 28), datetime.date(2011, 9, 28))

    def test_constructor_should_reject_none_start_date(self):
        try:
            DateRange(None, datetime.date(2011, 9, 28))
        except(TypeError):
            pass
        else:
            self.fail()

    def test_constructor_should_reject_none_end_date(self):
        try:
            DateRange(datetime.date(2011, 9, 28), None)
        except(TypeError):
            pass
        else:
            self.fail()

    def test_constructor_should_reject_end_date_before_start_date(self):
        date_before = datetime.date(2011, 8, 31)
        date_after = datetime.date(2011, 9, 28)
        try:
            DateRange(date_after, date_before)
        except(ValueError):
            pass
        else:
            self.fail()

    def test_constructor_should_reject_date_rime_start_date(self):
        try:
            DateRange(datetime(2011, 9, 28), datetime.date(2011, 9, 29))
        except(TypeError):
            pass
        else:
            self.fail()
        pass

    def test_constructor_should_reject_date_rime_end_date(self):
        try:
            DateRange(datetime.date(2011, 9, 28), datetime(2011, 9, 29))
        except(TypeError):
            pass
        else:
            self.fail()
        pass

    def test_start_date_should_return_constructed_Value(self):
        date_range = DateRange(datetime.date(2011, 9, 28), datetime.date(2011, 9, 29))
        self.assertEqual(datetime.date(2011, 9, 28), date_range.start_date)

    def test_end_date_should_return_constructed_Value(self):
        date_range = DateRange(datetime.date(2011, 9, 28), datetime.date(2011, 9, 29))
        self.assertEqual(datetime.date(2011, 9, 29), date_range.end_date)

    def test_start_date_should_be_immutable(self):
        date_range = DateRange(datetime.date(2011, 9, 28), datetime.date(2011, 9, 29))
        try:
            date_range.start_date = datetime.date(2011, 9, 27)
        except(AttributeError):
            pass
        else:
            self.fail()

    def test_end_date_should_be_immutable(self):
        date_range = DateRange(datetime.date(2011, 9, 28), datetime.date(2011, 9, 29))
        try:
            date_range.end_date = datetime.date(2011, 9, 30)
        except(AttributeError):
            pass
        else:
            self.fail()

    def test_date_range_for_year_should_start_jan_1(self):
        date_range = DateRange.for_year_containing(datetime.date(2011, 12, 11))
        self.assertEqual(datetime.date(2011, 1, 1), date_range.start_date)

    def test_date_range_for_year_should_end_dec_31(self):
        date_range = DateRange.for_year_containing(datetime.date(2011, 12, 11))
        self.assertEqual(datetime.date(2011, 12, 31), date_range.end_date)

    def test_date_range_for_month_should_start_first_day_of_month(self):
        date_range = DateRange.for_month_containing(datetime.date(2011, 12, 11))
        self.assertEqual(datetime.date(2011, 12, 1), date_range.start_date)

    def test_date_range_for_month_dec_should_end_dec_31(self):
        date_range = DateRange.for_month_containing(datetime.date(2011, 12, 11))
        self.assertEqual(datetime.date(2011, 12, 31), date_range.end_date)

    def test_date_range_for_month_feb_should_end_feb_28(self):
        date_range = DateRange.for_month_containing(datetime.date(2011, 2, 11))
        self.assertEqual(datetime.date(2011, 2, 28), date_range.end_date)

    def test_date_range_for_week_should_start_sunday(self):
        date_range = DateRange.for_week_containing(datetime.date(2011, 12, 7))
        self.assertEqual(datetime.date(2011, 12, 4), date_range.start_date)

    def test_date_range_for_week_should_end_saturday(self):
        date_range = DateRange.for_week_containing(datetime.date(2011, 12, 7))
        self.assertEqual(datetime.date(2011, 12, 10), date_range.end_date)
