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
from pytrainer.core.sport import Sport, SportService, SportServiceException
import mock
from pytrainer.lib.alchemyUtils import Sql
import pytrainer.core

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


class SportServiceTest(unittest.TestCase):
    
    def setUp(self):
        self.mock_ddbb = mock.Mock(spec=Sql)
        self.sport_service = SportService(self.mock_ddbb)
        
    def test_store_sport_should_insert_row_when_sport_has_no_id(self):
        def mock_select(table, columns, where):
            call_count = self.mock_ddbb.select.call_count
            if call_count == 2:
                return [[1]]
            return []
        self.mock_ddbb.select = mock.Mock(wraps=mock_select)
        sport = Sport()
        sport.name = u"Test name"
        self.sport_service.store_sport(sport)
        self.mock_ddbb.insert.assert_called_with("sports",  "name,weight,met,max_pace,color",
                                                 [u"Test name", 0.0, None, None, "0000ff"])
    
    def test_store_sport_should_update_row_when_sport_has_id(self):
        def mock_select(table, columns, where):
            if columns == "id_sports":
                return [[1]]
            else:
                return [(1, u"", 0, 0, 0, "0")]
        self.mock_ddbb.select = mock.Mock(wraps=mock_select)
        sport = Sport()
        sport.id = 1
        sport.name = u"New name"
        self.sport_service.store_sport(sport)
        self.mock_ddbb.update.assert_called_with("sports",  "name,weight,met,max_pace,color",
                                                 [u"New name", 0.0, None, None, "0000ff"], "id_sports=1")
        
    def test_store_sport_should_return_stored_sport(self):
        sport_ids = []
        def update_sport_ids(*args):
            sport_ids.append([1])
        self.mock_ddbb.insert.side_effect = update_sport_ids
        def mock_select(table, columns, where):
            if columns == "id_sports":
                return sport_ids
            else:
                return [(2, u"", 0, 0, 0, "0")]
        self.mock_ddbb.select = mock.Mock(wraps=mock_select)
        sport = Sport()
        stored_sport = self.sport_service.store_sport(sport)
        self.assertEquals(2, stored_sport.id)
    
    def test_store_sport_should_error_when_sport_has_unknown_id(self):
        self.mock_ddbb.select.return_value = []
        sport = Sport()
        sport.id = 100
        try:
            self.sport_service.store_sport(sport)
        except(SportServiceException):
            pass
        else:
            self.fail()
            
    def test_store_sport_should_error_when_new_sport_has_duplicate_name(self):
        self.mock_ddbb.select.return_value = [(1, u"Test name", 150, 12.5, 200, "0")]
        sport = Sport()
        sport.name = u"Test name"
        try:
            self.sport_service.store_sport(sport)
        except(SportServiceException):
            pass
        else:
            self.fail()

    def test_store_sport_should_error_when_existing_sport_has_duplicate_name(self):
        def mock_select(table, columns, where):
            if columns == pytrainer.core.sport._ID_COLUMN:
                return [[2]]
            else:
                return [(1, u"Test name", 0, 0.0, "0"), (2, u"New name", 0, 0.0, "0")]
        self.mock_ddbb.select = mock.Mock(wraps=mock_select)
        sport = Sport()
        sport.id = 1
        sport.name = u"New name"
        try:
            self.sport_service.store_sport(sport)
        except(SportServiceException):
            pass
        else:
            self.fail()
    
    def test_get_sport_returns_none_for_nonexistant_sport(self):
        self.mock_ddbb.select.return_value = []
        sport = self.sport_service.get_sport(1)
        self.assertEquals(None, sport)
        
    def test_get_sport_returns_sport_with_id(self):
        self.mock_ddbb.select.return_value = [(1, u"", 0, 0, 0, "0")]
        sport = self.sport_service.get_sport(1)
        self.assertEquals(1, sport.id)
        
    def test_get_sport_raises_error_for_id_none(self):
        try:
            self.sport_service.get_sport(None)
        except(ValueError):
            pass
        else:
            self.fail()
        
    def test_get_sport_by_name_returns_none_for_nonexistant_sport(self):
        self.mock_ddbb.select.return_value = []
        sport = self.sport_service.get_sport("no such sport")
        self.assertEquals(None, sport)
        
    def test_get_sport_by_name_returns_sport_with_name(self):
        def mock_select(table, columns, where):
            if columns == "id_sport":
                return [(1)]
            else:
                return [(1, u"rugby", 0, 0, 0, "0")]
        self.mock_ddbb.select = mock.Mock(wraps=mock_select)
        sport = self.sport_service.get_sport("rugby")
        self.assertEquals(u"rugby", sport.name)
        
    def test_get_sport_by_name_raises_error_for_none_sport_name(self):
        try:
            self.sport_service.get_sport_by_name(None)
        except(ValueError):
            pass
        else:
            self.fail()
        
    def test_get_all_sports_should_return_all_sports_in_query_result(self):
        self.mock_ddbb.select.return_value = [(1, u"Test name", 0, 0, 0, "0"), (2, u"Test name 2", 0, 0, 0, "0")]
        sports = self.sport_service.get_all_sports()
        self.assertEquals(2, len(sports))
        sport1 = sports[0]
        self.assertEquals(1, sport1.id)
        sport2 = sports[1]
        self.assertEquals(2, sport2.id)
    
    def test_get_all_sports_should_return_no_sports_when_query_result_empty(self):
        self.mock_ddbb.select.return_value = []
        sports = self.sport_service.get_all_sports()
        self.assertEquals(0, len(sports))
        
    def test_remove_sport_should_error_when_sport_has_no_id(self):
        self.mock_ddbb.select.return_value = [(1, u"Test name", 150, 12.5, 200, "0")]
        sport = Sport()
        try:
            self.sport_service.remove_sport(sport)
        except(SportServiceException):
            pass
        else:
            self.fail()
        
    def test_remove_sport_should_error_when_sport_has_unknown_id(self):
        self.mock_ddbb.select.return_value = []
        sport = Sport()
        sport.id = 100
        try:
            self.sport_service.remove_sport(sport)
        except(SportServiceException):
            pass
        else:
            self.fail()
            
    def test_remove_sport_should_delete_sport_with_specified_id(self):
        self.mock_ddbb.select.return_value = [[1]]
        sport = Sport()
        sport.id = 1
        self.sport_service.remove_sport(sport)
        self.mock_ddbb.delete.assert_called_with("sports", "id_sports=1")

    def test_remove_sport_should_remove_associated_entries(self):
        self.mock_ddbb.select.return_value = [[1]]
        sport = Sport()
        sport.id = 1
        delete_arguments = []
        def mock_delete(*args):
            delete_arguments.append(args) 
        self.mock_ddbb.delete = mock.Mock(wraps=mock_delete)
        self.sport_service.remove_sport(sport)
        self.assertEquals(("records", "sport=1"), delete_arguments[0])
