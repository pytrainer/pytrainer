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

from pytrainer.lib.color import Color

class Sport(object):
    
    """A type of exercise. For example: "running" or "cycling"."""
    
    def __init__(self):
        self._id = None
        self.name = u""
        self.weight = 0.0
        self.met = None
        self.max_pace = None
        self.color = Color(0x0000ff)
       
    def _get_id(self):
        return self._id
    
    def _set_id(self, id):
        self._id = int(id)
    
    id = property(_get_id, _set_id)
       
    def _get_name(self):
        return self._name
    
    def _set_name(self, name):
        if not isinstance(name, unicode):
            raise TypeError("Name must be unicode string, not {0}.".format(type(name).__name__))
        self._name = name
    
    name = property(_get_name, _set_name)
       
    def _get_weight(self):
        return self._weight
    
    def _set_weight(self, weight):
        weight_float = float(weight)
        if weight_float < 0:
            raise ValueError("Weight must not be negative.")
        self._weight = weight_float
    
    weight = property(_get_weight, _set_weight)
       
    def _get_met(self):
        return self._met
    
    def _set_met(self, met):
        met_float = float(met) if met is not None else None
        if met_float is not None and met_float < 0:
            raise ValueError("MET must not be negative.")
        self._met = met_float
    
    met = property(_get_met, _set_met)
       
    def _get_max_pace(self):
        return self._max_pace
    
    def _set_max_pace(self, max_pace):
        max_pace_int = int(max_pace) if max_pace is not None else None
        if max_pace_int is not None and max_pace_int < 0:
            raise ValueError("Max pace must not be negative.")
        self._max_pace = max_pace_int
    
    max_pace = property(_get_max_pace, _set_max_pace)
    
    def _get_color(self):
        return self._color
    
    def _set_color(self, color):
        if color is None:
            raise ValueError("Color must be valued.")
        self._color = color
        
    color = property(_get_color, _set_color)
