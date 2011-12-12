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

import datetime
from subprocess import Popen, PIPE

class DateRange(object):
    
    """A date range consisting of a start date and an end date."""
    
    def __init__(self, start_date, end_date):
        if not isinstance(start_date, datetime.date):
            raise TypeError("Start date must be datetime.date, not {0}.".format(type(start_date).__name__))
        if not isinstance(end_date, datetime.date):
            raise TypeError("End date must be datetime.date, not {0}.".format(type(start_date).__name__))
        if cmp(start_date, end_date) > 0:
            raise ValueError("End date cannot be before start date.")
        self._start_date = start_date
        self._end_date = end_date
        
    @property
    def start_date(self):
        return self._start_date
    
    @property
    def end_date(self):
        return self._end_date
    
    def __str__(self):
        fmt = "%Y%m%d"
        return self._start_date.strftime(fmt) + "-" + self._end_date.strftime(fmt)

    @classmethod
    def for_week_containing(clazz, date):
        """Get the date range for the week containing the given date.
        
        The date range will start on the first day of the week and end on the
        last day of the week. The week start and end days are locale dependent.
        
        Args:
            date (datetime.date): a date within the week to get the date range for.
        Returns:
            (DateRange): the date range for a week.
        """
        day_of_week = (int(date.strftime("%w")) - first_day_of_week()) % 7
        date_start = date + datetime.timedelta(days = 0 - day_of_week)
        date_end = date + datetime.timedelta(days = 6 - day_of_week)
        return DateRange(date_start, date_end)
    
    @classmethod
    def for_month_containing(clazz, date):
        """Get the date range for the month containing the given date.
        
        The date range will start on the first day of the month and end on the
        last day of the month.
        
        Args:
            date (datetime.date): a date within the month to get the date range for.
        Returns:
            (DateRange): the date range for a month.
        """
        date_start = datetime.date(date.year, date.month, 1)
        next_month = date.month + 1
        next_month_year = date.year
        if (next_month == 13):
            next_month = 1
            next_month_year += 1
        date_end = datetime.date(next_month_year, next_month, 1) - datetime.timedelta(days=1)
        return DateRange(date_start, date_end)
    
    @classmethod
    def for_year_containing(clazz, date):
        """Get the date range for the year containing the given date.
        
        The date range will start on the first day of the year and end on the
        last day of the year.
        
        Args:
            date (datetime.date): a date within the year to get the date range for.
        Returns:
            (DateRange): the date range for a year.
        """
        date_start = datetime.date(date.year, 1, 1)
        date_end = datetime.date(date.year, 12, 31)
        return DateRange(date_start, date_end)
    
def first_day_of_week():
    """Determine the first day of the week for the system locale.
    
    If the first day of the week cannot be determined then Sunday is assumed.
    
    Returns (int): a day of the week; 0: Sunday, 1: Monday, 6: Saturday.
    """
    # Python's locale does not have a first day of week so make a system call
    # http://blogs.gnome.org/patrys/2008/09/29/how-to-determine-the-first-day-of-week/
    CMD=("locale", "first_weekday", "week-1stday")
    process = Popen(CMD, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if  process.returncode != 0:
        return 0
    results = stdout.split("\n")
    if len(results) < 2:
        return 0
    day_delta = datetime.timedelta(days=int(results[0]) - 1)
    base_date = datetime.datetime.strptime(results[1], "%Y%m%d")
    first_day = base_date + day_delta
    return int(first_day.strftime("%w"))
