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

class Color(object):
    
    """A color represented as a 24-bit RGB value."""
    
    def __init__(self, rgb_val=0):
        rgb_val_int = int(rgb_val)
        if rgb_val_int < 0:
            raise ValueError("RGB value must not be negative.")
        if rgb_val_int > 0xffffff:
            raise ValueError("RGB value must not be greater than 0xffffff.")
        self._rgb_val = rgb_val_int
        
    def _get_rgb_val(self):
        return self._rgb_val
    
    rgb_val = property(_get_rgb_val)
        
    def _get_rgba_val(self):
        return self._rgb_val << 8
    
    rgba_val = property(_get_rgba_val)
    
    def to_hex_string(self):
        return "{0:06x}".format(self._rgb_val)
    
def color_from_hex_string(hex_string):
    return Color(int(hex_string, 16))
