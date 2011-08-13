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

from pytrainer.lib.color import Color, color_from_hex_string
import unittest

class ColorTest(unittest.TestCase):
    
    def test_constructor_should_accept_integer(self):
        color = Color(12345)
        self.assertEqual(12345, color.rgb_val)
    
    def test_constructor_should_accept_integer_string(self):
        color = Color("12345")
        self.assertEqual(12345, color.rgb_val)
    
    def test_constructor_should_not_accept_non_integer_string(self):
        try:
            Color("ff00ff")
        except(ValueError):
            pass
        else:
            self.fail()
    
    def test_constructor_should_not_accept_none(self):
        try:
            Color(None)
        except(TypeError):
            pass
        else:
            self.fail()
    
    def test_constructor_should_not_accept_negative_value(self):
        try:
            Color(-1)
        except(ValueError):
            pass
        else:
            self.fail()
            
    def test_constructor_should_not_accept_value_over_24_bit(self):
        try:
            Color(2 ** 24)
        except(ValueError):
            pass
        else:
            self.fail()

    def test_rgb_value_should_default_to_0(self):
        color = Color()
        self.assertEqual(0, color.rgb_val)
            
    def test_rgb_value_should_be_read_only(self):
        color = Color()
        try:
            color.rgb_val = 1
        except(AttributeError):
            pass
        else:
            self.fail()
            
    def test_rgba_value_should_be_rgb_value_with_two_trailing_zero_hex_digits(self):
        color = Color(0x1177ff)
        self.assertEquals(0x1177ff00, color.rgba_val)
        
    def test_to_hex_string_should_create_six_digit_hex_value(self):
        color = Color(0xfab)
        self.assertEquals("000fab", color.to_hex_string())
        
    def test_color_from_hex_string_should_correctly_decode_hex_value(self):
        color = color_from_hex_string("fab")
        self.assertEquals(0xfab, color.rgb_val)
