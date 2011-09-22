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
