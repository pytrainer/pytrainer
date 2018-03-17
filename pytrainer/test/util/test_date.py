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
import pytrainer.util.date
from pytrainer.util.date import DateRange
from datetime import date
from datetime import datetime
from mock import Mock

class DateRangeTest(unittest.TestCase):
    
    def setUp(self):
        pytrainer.util.date.first_day_of_week = Mock()
        pytrainer.util.date.first_day_of_week.return_value = 0

    def test_constructor_should_accept_end_date_same_as_start_date(self):
        DateRange(date(2011, 9, 28), date(2011, 9, 28))

    def test_constructor_should_reject_none_start_date(self):
        try:
            DateRange(None, date(2011, 9, 28))
        except(TypeError):
            pass
        else:
            self.fail()

    def test_constructor_should_reject_none_end_date(self):
        try:
            DateRange(date(2011, 9, 28), None)
        except(TypeError):
            pass
        else:
            self.fail()

    def test_constructor_should_reject_end_date_before_start_date(self):
        date_before = date(2011, 8, 31)
        date_after = date(2011, 9, 28)
        try:
            DateRange(date_after, date_before)
        except(ValueError):
            pass
        else:
            self.fail()
    
    def test_constructor_should_reject_date_rime_start_date(self):
        try:
            DateRange(datetime(2011, 9, 28), date(2011, 9, 29))
        except(TypeError):
            pass
        else:
            self.fail()
        pass
    
    def test_constructor_should_reject_date_rime_end_date(self):
        try:
            DateRange(date(2011, 9, 28), datetime(2011, 9, 29))
        except(TypeError):
            pass
        else:
            self.fail()
        pass
    
    def test_start_date_should_return_constructed_Value(self):
        date_range = DateRange(date(2011, 9, 28), date(2011, 9, 29))
        self.assertEquals(date(2011, 9, 28), date_range.start_date)
    
    def test_end_date_should_return_constructed_Value(self):
        date_range = DateRange(date(2011, 9, 28), date(2011, 9, 29))
        self.assertEquals(date(2011, 9, 29), date_range.end_date)
    
    def test_start_date_should_be_immutable(self):
        date_range = DateRange(date(2011, 9, 28), date(2011, 9, 29))
        try:
            date_range.start_date = date(2011, 9, 27)
        except(AttributeError):
            pass
        else:
            self.fail()
    
    def test_end_date_should_be_immutable(self):
        date_range = DateRange(date(2011, 9, 28), date(2011, 9, 29))
        try:
            date_range.end_date = date(2011, 9, 30)
        except(AttributeError):
            pass
        else:
            self.fail()
            
    def test_date_range_for_year_should_start_jan_1(self):
        date_range = DateRange.for_year_containing(date(2011, 12, 11))
        self.assertEquals(date(2011, 1, 1), date_range.start_date)
    
    def test_date_range_for_year_should_end_dec_31(self):
        date_range = DateRange.for_year_containing(date(2011, 12, 11))
        self.assertEquals(date(2011, 12, 31), date_range.end_date)
        
    def test_date_range_for_month_should_start_first_day_of_month(self):
        date_range = DateRange.for_month_containing(date(2011, 12, 11))
        self.assertEquals(date(2011, 12, 1), date_range.start_date)
        
    def test_date_range_for_month_dec_should_end_dec_31(self):
        date_range = DateRange.for_month_containing(date(2011, 12, 11))
        self.assertEquals(date(2011, 12, 31), date_range.end_date)
        
    def test_date_range_for_month_feb_should_end_feb_28(self):
        date_range = DateRange.for_month_containing(date(2011, 2, 11))
        self.assertEquals(date(2011, 2, 28), date_range.end_date)
        
    def test_date_range_for_week_should_start_sunday(self):
        date_range = DateRange.for_week_containing(date(2011, 12, 7))
        self.assertEquals(date(2011, 12, 4), date_range.start_date)
    
    def test_date_range_for_week_should_end_saturday(self):
        date_range = DateRange.for_week_containing(date(2011, 12, 7))
        self.assertEquals(date(2011, 12, 10), date_range.end_date)
        
