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

from gi.repository import Gdk
from pytrainer.util.color import Color

class ColorConverter(object):
    
    """Converts between Pytrainer and GDK color instances.""" 
    
    def convert_to_gdk_rgba(self, color: Color) -> Gdk.RGBA:
        """Convert a Pytrainer color to a GDK.RGBA."""
        color_format = "#{0:06x}".format(color.rgb_val)
        _rgba = Gdk.RGBA()
        _rgba.parse(color_format)
        return _rgba
    
    def convert_to_color(self, gdk_col: Gdk.RGBA) -> Color:
        """Convert a GDK.RGBA to a Pytrainer color."""
        red = round(gdk_col.red * 255)
        green = round(gdk_col.green * 255)
        blue = round(gdk_col.blue * 255)
        rgb_val = (red << 16) + (green << 8) + blue
        return Color(rgb_val)
