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
from dateutil.tz import * # for tzutc()
import logging

def second2time(seconds):
    if not seconds:
        return 0,0,0
    #time_in_hour = seconds/3600.0
    #hour = int(time_in_hour)
    #min = int((time_in_hour-hour)*60)
    #sec = (((time_in_hour-hour)*60)-min)*60
    #sec = seconds-(hour*3600)-(min*60)
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
    monthName = calendar.month_name[date.month]
    return monthName, daysInMonth

def unixtime2date(unixtime):
    print unixtime
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
        print "Unable to parse '%s' as a date time" % time_
        print e
        logging.debug("Unable to parse %s as a date time" % time_)
        logging.debug(str(e))
        return (None, None)
    timezone = dateTime.tzinfo
    if timezone is None: #got a naive time, so assume is local time
        #print 'Naive time'
        local_dateTime = dateTime.replace(tzinfo=tzlocal())
    elif timezone == tzutc(): #got a zulu time
        #print 'zulu time'
        local_dateTime = dateTime.astimezone(tzlocal()) #datetime with localtime offset (from OS)
    else:
        #print 'local time'
        local_dateTime = dateTime #use datetime as supplied
    utc_dateTime = local_dateTime.astimezone(tzutc()) #datetime with 00:00 offset
    #print utc_dateTime, local_dateTime
    return (utc_dateTime,local_dateTime)

class Date:
    def __init__(self, calendar=None):
        self.calendar = calendar
        self.second2time = second2time
        self.time2second = time2second
        self.getLocalTZ = getLocalTZ
        self.time2string = time2string
        self.getNameMonth = getNameMonth
        self.unixtime2date = unixtime2date
        self.getDateTime = getDateTime

    def getDate(self):
        #hack for the gtk calendar widget
        if self.calendar is not None:
            year,month,day = self.calendar.get_date()
            return datetime.date(year, month+1, day)
        else:
            return datetime.date.today()

    def setDate(self,newdate):
        year,month,day = newdate.split("-")
        self.calendar.select_month(int(month)-1,int(year))
        self.calendar.select_day(int(day))
