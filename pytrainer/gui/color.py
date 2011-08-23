# -*- coding: utf-8 -*-

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

import gtk.gdk
from pytrainer.util.color import Color

class ColorConverter(object):
    
    """Converts between Pytrainer and GDK color instances.""" 
    
    def convert_to_gdk_color(self, color):
        """Convert a Pytrainer color to a GDK color."""
        color_format = "#{0:06x}".format(color.rgb_val)
        return gtk.gdk.color_parse(color_format)
    
    def convert_to_color(self, gdk_col):
        """Convert a GDK color to a Pytrainer color."""
        red = gdk_col.red >> 8
        green = gdk_col.green >> 8
        blue = gdk_col.blue >> 8
        rgb_val = (red << 16) + (green << 8) + blue
        return Color(rgb_val)
