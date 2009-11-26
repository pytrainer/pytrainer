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

class Date:
	def __init__(self, calendar=None):
		self.calendar = calendar
	
	def second2time(self,seconds):
		time_in_hour = seconds/3600.0
		hour = int(time_in_hour)
		min = int((time_in_hour-hour)*60)
		sec = (((time_in_hour-hour)*60)-min)*60
		sec = seconds-(hour*3600)-(min*60)
		return hour,min,sec

	def time2second(self,time):
		hour,min,sec = time
		return sec+(min*60)+(hour*3600)

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

	def getWeekInterval(self,date, prf_us_system):
		''' Function to provide beginning and ending of the week that a certain day is in
			Problems as python date functions do not respect locale (i.e. Sunday is always start of week????)
			Note: %w gives weekday as a decimal number [0(Sunday),6(Saturday)].
		'''
		if prf_us_system == "True":
			#Sunday is first day of week
			weekDate = datetime.datetime.strptime(date, "%Y-%m-%d")
			dayOfWeek = int(weekDate.strftime("%w"))
		else:
			#Monday is first day of week
			weekDate = datetime.datetime.strptime(date, "%Y-%m-%d")
			dayOfWeek = int(weekDate.strftime("%w"))
			if dayOfWeek == 0: #Sunday, need to adjust
				dayOfWeek = 7
			dayOfWeek -= 1
		date_ini = weekDate + datetime.timedelta(days=0-dayOfWeek)
		date_end = weekDate + datetime.timedelta(days=6-dayOfWeek)
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
		#	"01":_("January"),
		#	"02":_("Febrary"),
		#	"03":_("March"),
		#	"04":_("April"),
		#	"05":_("May"),
		#	"06":_("June"),
		#	"07":_("July"),
		#	"08":_("August"),
		#	"09":_("September"),
		#	"10":_("October"),
		#	"11":_("November"),
		#	"12":_("December")
		#	}
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

