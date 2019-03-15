# -*- coding: iso-8859-1 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net
# vud1@grupoikusnet.com
# Jakinbidea & Grupo Ikusnet Developer

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

import time
import datetime
import calendar
import dateutil.parser
from dateutil.tz import tzutc, tzlocal
import logging

from pytrainer.platform import get_platform
from pytrainer.lib.localization import locale_str

def second2time(seconds):
    if not seconds:
        return 0,0,0
    hours = seconds // (60*60)
    seconds %= (60*60)
    minutes = seconds // 60
    seconds %= 60
    return hours,minutes,seconds

def time2second(time):
    hour,min,sec = time
    return int(sec)+(int(min)*60)+(int(hour)*3600)

def getLocalTZ():
    ''' Returns string representation of local timezone'''
    return datetime.datetime.now(tzlocal()).tzname()

def time2string(date):
    return "%0.4d-%0.2d-%0.2d" %(int(date[0]),int(date[1]),int(date[2]))

def getNameMonth(date):
    day, daysInMonth = calendar.monthrange(date.year, date.month)
    monthName = locale_str(calendar.month_name[date.month])
    return monthName, daysInMonth

def unixtime2date(unixtime):
    tm = time.gmtime(unixtime)
    year = tm[0]
    month = tm[1]
    day = tm[2]
    return "%0.4d-%0.2d-%0.2d" %(year,month,day)

def getDateTime(time_):
    # Time can be in multiple formats
    # - zulu            2009-12-15T09:00Z
    # - local ISO8601   2009-12-15T10:00+01:00
    try:
        dateTime = dateutil.parser.parse(time_)
    except ValueError as e:
        logging.debug("Unable to parse %s as a date time" % time_)
        logging.debug(str(e))
        return (None, None)
    timezone = dateTime.tzinfo
    if timezone is None: #got a naive time, so assume is local time
        local_dateTime = dateTime.replace(tzinfo=tzlocal())
    elif timezone == tzutc(): #got a zulu time
        local_dateTime = dateTime.astimezone(tzlocal()) #datetime with localtime offset (from OS)
    else:
        local_dateTime = dateTime #use datetime as supplied
    utc_dateTime = local_dateTime.astimezone(tzutc()) #datetime with 00:00 offset
    return (utc_dateTime,local_dateTime)

class Date:
    def __init__(self, calendar=None):
        self.calendar = calendar

    def getDate(self):
        #hack for the gtk calendar widget
        if self.calendar is not None:
            year,month,day = self.calendar.get_date()
            # Selected day might be larger than current month's number of days.
            # Iterate backwards until we find valid date.
            while day > 1:
                try:
                    return datetime.date(year, month + 1, day)
                except ValueError:
                    day -= 1
            raise ValueError("Invalid date supplied: "
                             "day is before 1st of month.")
        else:
            return datetime.date.today()

    def setDate(self,newdate):
        year,month,day = newdate.split("-")
        self.calendar.select_month(int(month)-1,int(year))
        self.calendar.select_day(int(day))

class DateRange(object):

    """A date range consisting of a start date and an end date."""

    def __init__(self, start_date, end_date):
        if not isinstance(start_date, datetime.date):
            raise TypeError("Start date must be datetime.date, not {0}.".format(type(start_date).__name__))
        if not isinstance(end_date, datetime.date):
            raise TypeError("End date must be datetime.date, not {0}.".format(type(start_date).__name__))
        if start_date > end_date:
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
        day_of_week = (int(date.strftime("%w")) - get_platform().get_first_day_of_week()) % 7
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
