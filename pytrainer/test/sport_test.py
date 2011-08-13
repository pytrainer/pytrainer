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

import unittest
from pytrainer.sport import Sport

class SportTest(unittest.TestCase):
    
    def test_id_should_default_to_none(self):
        sport = Sport()
        self.assertEquals(None, sport.id)
        
    def test_id_should_accept_integer(self):
        sport = Sport()
        sport.id = 1
        self.assertEquals(1, sport.id)
        
    def test_id_should_accept_integer_string(self):
        sport = Sport()
        sport.id = "1"
        self.assertEquals(1, sport.id)
        
    def test_id_should_not_accept_non_integer_string(self):
        sport = Sport()
        try:
            sport.id = "1.1"
        except(ValueError):
            pass
        else:
            self.fail()
            
    def test_id_should_not_accept_none(self):
        sport = Sport()
        try:
            sport.id = None
        except(TypeError):
            pass
        else:
            self.fail()
        
    def test_name_should_default_to_empty_string(self):
        sport = Sport()
        self.assertEquals(u"", sport.name)
        
    def test_name_should_accept_unicode_string(self):
        sport = Sport()
        sport.name = u"Unicycling"
        self.assertEquals(u"Unicycling", sport.name)
        
    def test_name_should_not_accept_non_unicode_string(self):
        sport = Sport()
        try:
            sport.name = "Juggling"
        except(TypeError):
            pass
        else:
            self.fail()
            
    def test_name_should_not_accept_none(self):
        sport = Sport()
        try:
            sport.name = None
        except(TypeError):
            pass
        else:
            self.fail()
            
    def test_met_should_default_to_None(self):
        sport = Sport()
        self.assertEquals(None, sport.met)
        
    def test_met_should_accept_float(self):
        sport = Sport()
        sport.met = 22.5
        self.assertEquals(22.5, sport.met)
        
    def test_met_should_accept_float_string(self):
        sport = Sport()
        sport.met = "22.5"
        self.assertEquals(22.5, sport.met)
        
    def test_met_should_not_accept_non_float_string(self):
        sport = Sport()
        try:
            sport.met = "22.5kg"
        except(ValueError):
            pass
        else:
            self.fail()
                     
    def test_met_should_not_accept_negative_value(self):
        sport = Sport()
        try:
            sport.met = -1
        except(ValueError):
            pass
        else:
            self.fail()
            
    def test_met_should_accept_none(self):
        sport = Sport()
        sport.met = None
        self.assertEquals(None, sport.met)
            
    def test_weight_should_default_to_zero(self):
        sport = Sport()
        self.assertEquals(0, sport.weight)
        
    def test_weight_should_accept_float(self):
        sport = Sport()
        sport.weight = 22.5
        self.assertEquals(22.5, sport.weight)
        
    def test_weight_should_accept_float_string(self):
        sport = Sport()
        sport.weight = "22.5"
        self.assertEquals(22.5, sport.weight)
        
    def test_weight_should_not_accept_non_float_string(self):
        sport = Sport()
        try:
            sport.weight = "22.5kg"
        except(ValueError):
            pass
        else:
            self.fail()
            
    def test_weight_should_not_accept_negative_value(self):
        sport = Sport()
        try:
            sport.weight = -1
        except(ValueError):
            pass
        else:
            self.fail()
            
    def test_weight_should_not_accept_none(self):
        sport = Sport()
        try:
            sport.weight = None
        except(TypeError):
            pass
        else:
            self.fail()
            
    def test_max_pace_should_default_to_none(self):
        sport = Sport()
        self.assertEquals(None, sport.max_pace)
        
    def test_max_pace_should_accept_integer(self):
        sport = Sport()
        sport.max_pace = 220
        self.assertEquals(220, sport.max_pace)
        
    def test_max_pace_should_accept_integer_string(self):
        sport = Sport()
        sport.max_pace = "220"
        self.assertEquals(220, sport.max_pace)
        
    def test_max_pace_should_not_accept_non_integer_string(self):
        sport = Sport()
        try:
            sport.max_pace = "225s"
        except(ValueError):
            pass
        else:
            self.fail()
        
    def test_max_pace_should_take_floor_of_float(self):
        sport = Sport()
        sport.max_pace = 220.6
        self.assertEquals(220, sport.max_pace)
            
    def test_max_pace_should_not_accept_negative_value(self):
        sport = Sport()
        try:
            sport.max_pace = -1
        except(ValueError):
            pass
        else:
            self.fail()
            
    def test_max_pace_should_accept_none(self):
        sport = Sport()
        sport.max_pace = None
        self.assertEquals(None, sport.max_pace)
        
    def test_color_should_default_to_blue(self):
        sport = Sport()
        self.assertEquals(0x0000ff, sport.color.rgb_val)
        
    def test_color_should_not_accept_none(self):
        sport = Sport()
        try:
            sport.color = None
        except(ValueError):
            pass
        else:
            self.fail()
