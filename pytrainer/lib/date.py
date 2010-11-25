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
import datetime
import dateutil.parser
from dateutil.tz import * # for tzutc()
from subprocess import Popen, PIPE

class Date:
    def __init__(self, calendar=None):
        self.calendar = calendar
    
    def second2time(self,seconds):
        if not seconds:
            return 0,0,0
        time_in_hour = seconds/3600.0
        hour = int(time_in_hour)
        min = int((time_in_hour-hour)*60)
        sec = (((time_in_hour-hour)*60)-min)*60
        sec = seconds-(hour*3600)-(min*60)
        return hour,min,sec

    def time2second(self,time):
        hour,min,sec = time
        return int(sec)+(int(min)*60)+(int(hour)*3600)

    def getLocalTZ(self):
        ''' Returns string representation of local timezone'''
        return datetime.datetime.now(tzlocal()).tzname()

    def getDate(self):
        #hack for the gtk calendar widget
        if self.calendar is not None:
            year,month,day = self.calendar.get_date()
            return "%0.4d-%0.2d-%0.2d" %(year,month+1,day)
        else:
            return datetime.date.today().strftime("%Y-%m-%d")

    def setDate(self,newdate):
        year,month,day = newdate.split("-")
        self.calendar.select_month(int(month)-1,int(year))
        self.calendar.select_day(int(day))
    
    def time2string(self,date):
        return "%0.4d-%0.2d-%0.2d" %(int(date[0]),int(date[1]),int(date[2]))
        
    def getFirstDayOfWeek(self):
        '''
        Function to determine the first day of the week from the locale
        from http://blogs.gnome.org/patrys/2008/09/29/how-to-determine-the-first-day-of-week/
        
        $ locale first_weekday week-1stday
        2
        19971130
        '''
        
        CMD=('locale', 'first_weekday', 'week-1stday')
        p=Popen(CMD, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        #print "STDOUT\n"+stdout
        #print "STDERR\n"+stderr
        #print "RETURNCODE: "+str(p.returncode)
        if  p.returncode != 0:
            #Error in command execution
            return None
        results = stdout.split('\n')
        if len(results) < 2:
            #print "len error", len(results), results
            return None
        try:
            day_delta = datetime.timedelta(days=int(results[0]) - 1)
            base_date = dateutil.parser.parse(results[1])
            first_day = base_date + day_delta
            logging.debug("First day of week based on locale is:", first_day.strftime("%A"))
            return first_day
        except Exception as e:
            print type(e)
            print e
            return None
        
        

    def getWeekInterval(self,date, prf_us_system):
        ''' Function to provide beginning and ending of the week that a certain day is in
            Problems as python date functions do not respect locale (i.e. Sunday is always start of week????)
            Note: %w gives weekday as a decimal number [0(Sunday),6(Saturday)].
        '''
        weekDate = datetime.datetime.strptime(date, "%Y-%m-%d")
        dayOfWeek = int(weekDate.strftime("%w"))
        #print "Today is %s day of the week:" % dayOfWeek
        first_day = self.getFirstDayOfWeek().strftime("%w") #0 = Sun is first, 1 = Mon is first, 6 = Sat is first
        #first_day = 6
        if first_day is not None:
            #got response from locale query...
            #print "first day of week is:", first_day
            #Adjust dayOfweek...
            dayOfWeek -= int(first_day)
            if dayOfWeek < 0:
                dayOfWeek += 7
            #print "Adjusted today is %s day of the week:" % dayOfWeek
        date_ini = weekDate + datetime.timedelta(days=0-dayOfWeek)
        date_end = weekDate + datetime.timedelta(days=6-dayOfWeek)
        #print "weekrange", date_ini.strftime("%A"), date_end.strftime("%A")
        #print "dates", date_ini.strftime("%Y-%m-%d"), date_end.strftime("%Y-%m-%d")
        return date_ini.strftime("%Y-%m-%d"), date_end.strftime("%Y-%m-%d")
    
    def getMonthInterval(self,date):
        year,month,day = date.split("-")
        date_ini = "%0.4d-%0.2d-00" %(int(year),int(month))
        if (int(month)<12):
            month = int(month)+1
        else:
            year = int(year)+1
            month = 1
        date_end = "%0.4d-%0.2d-01" %(int(year),int(month))
        return date_ini, date_end

    def getYearInterval(self,date):
        year,month,day = date.split("-")
        date_ini = "%0.4d-0.1-01" %int(year)
        year = int(year)+1
        date_end = "%0.4d-01-01" %int(year)
        return date_ini, date_end
    
    def getNameMonth(self, date):
        #month_name = {
        #   "01":_("January"),
        #   "02":_("Febrary"),
        #   "03":_("March"),
        #   "04":_("April"),
        #   "05":_("May"),
        #   "06":_("June"),
        #   "07":_("July"),
        #   "08":_("August"),
        #   "09":_("September"),
        #   "10":_("October"),
        #   "11":_("November"),
        #   "12":_("December")
        #   }
        year,month,day = date.split("-")
        day, daysInMonth = calendar.monthrange(int(year), int(month))
        monthName = calendar.month_name[int(month)]
        return monthName, daysInMonth

    def getYear(self,date):
        year,month,day = date.split("-")
        return year

    def unixtime2date(self,unixtime):
        print unixtime
        tm = time.gmtime(unixtime)
        year = tm[0]                
        month = tm[1]               
        day = tm[2]
        return "%0.4d-%0.2d-%0.2d" %(year,month,day)

    def getDateTime(self, time_):
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

