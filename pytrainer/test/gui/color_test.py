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

from pytrainer.gui.color import ColorConverter
from pytrainer.lib.color import Color
import gtk.gdk
import unittest

class ColorConverterTest(unittest.TestCase):
    
    def setUp(self):
        self._converter = ColorConverter()
    
    def test_convert_to_gdk_color_should_create_gdk_color_with_equivalent_rgb_values(self):
        color = Color(0xaaff33)
        gdk_color = self._converter.convert_to_gdk_color(color)
        self.assertEquals(0x3333, gdk_color.blue)
        self.assertEquals(0xffff, gdk_color.green)
        self.assertEquals(0xaaaa, gdk_color.red)
        
    def test_convert_to_color_should_create_color_with_equivalent_rgb_values(self):
        gdk_col = gtk.gdk.color_parse("#aaff33")
        color = self._converter.convert_to_color(gdk_col)
        self.assertEqual(0xaaff33, color.rgb_val)
