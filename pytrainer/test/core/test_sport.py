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
import sys
from pytrainer.core.sport import Sport, SportService, SportServiceException
import pytrainer.core
from pytrainer.lib.ddbb import DDBB
from sqlalchemy.exc import IntegrityError, StatementError, ProgrammingError, OperationalError, InterfaceError, DataError

class SportTest(unittest.TestCase):

    def setUp(self):
        self.ddbb = DDBB()
        self.ddbb.connect()
        self.ddbb.create_tables(add_default=False)

    def tearDown(self):
        self.ddbb.disconnect()
        self.ddbb.drop_tables()
    
    def test_id_should_default_to_none(self):
        sport = Sport()
        self.assertEqual(None, sport.id)
        
    def test_id_should_accept_integer(self):
        sport = Sport()
        sport.id = 1
        self.assertEqual(1, sport.id)
        
    def test_id_should_accept_integer_string(self):
        sport = Sport()
        sport.id = "1"
        self.ddbb.session.add(sport)
        self.ddbb.session.commit()
        sport = self.ddbb.session.query(Sport).filter(Sport.id == 1).one()
        self.assertEqual(1, sport.id)
        
    def test_id_should_not_accept_non_integer_string(self):
        sport = Sport()
        try:
            sport.id = "test"
            self.ddbb.session.add(sport)
            self.ddbb.session.flush()
        except (IntegrityError, DataError, OperationalError):
            pass
        else:
            self.fail()
            
    def test_name_should_default_to_empty_string(self):
        sport = Sport()
        self.assertEqual(u"", sport.name)
        
    def test_name_should_accept_unicode_string(self):
        sport = Sport()
        sport.name = u"Unicycling"
        self.assertEqual(u"Unicycling", sport.name)

    @unittest.skipIf(sys.version_info > (3, 0), "All strings are unicode in Python 3")
    def test_name_should_not_accept_non_unicode_string(self):
        sport = Sport()
        sport.name = "Juggling" + chr(255)
        try:
            self.ddbb.session.add(sport)
            self.ddbb.session.flush()
        except (ProgrammingError, DataError, OperationalError):
            pass
        else:
            self.fail()
            
    def test_name_should_not_accept_none(self):
        sport = Sport()
        sport.name = None
        try:
            self.ddbb.session.add(sport)
            self.ddbb.session.commit()
        except (IntegrityError, OperationalError):
            pass
        else:
            self.fail()
            
    def test_met_should_default_to_None(self):
        sport = Sport()
        self.assertEqual(None, sport.met)
        
    def test_met_should_accept_float(self):
        sport = Sport()
        sport.met = 22.5
        self.ddbb.session.add(sport)
        self.ddbb.session.flush()
        self.assertEqual(22.5, sport.met)
        
    def test_met_should_accept_float_string(self):
        sport = Sport()
        sport.name = "test1"
        sport.met = "22.5"
        self.ddbb.session.add(sport)
        self.ddbb.session.commit()
        sport = self.ddbb.session.query(Sport).filter(Sport.id == 1).one()
        self.assertEqual(22.5, sport.met)
        
    def test_met_should_not_accept_non_float_string(self):
        sport = Sport()
        sport.met = "22.5kg"
        try:
            self.ddbb.session.add(sport)
            self.ddbb.session.flush()
        except(ValueError, StatementError):
            pass
        else:
            self.fail()
                     
    def test_met_should_not_accept_negative_value(self):
        if self.ddbb.engine.name == 'mysql':
            self.skipTest('Check constraints not available on Mysql')
        sport = Sport()
        sport.met = -1
        try:
            self.ddbb.session.add(sport)
            self.ddbb.session.flush()
        except (IntegrityError, InterfaceError):
            pass
        else:
            self.fail()
            
    def test_met_should_accept_none(self):
        sport = Sport()
        sport.met = None
        self.assertEqual(None, sport.met)
            
    def test_weight_should_default_to_zero(self):
        sport = Sport()
        self.assertEqual(0, sport.weight)
        
    def test_weight_should_accept_float(self):
        sport = Sport()
        sport.weight = 22.5
        self.assertEqual(22.5, sport.weight)
        
    def test_weight_should_accept_float_string(self):
        sport = Sport()
        sport.weight = "22.5"
        self.ddbb.session.add(sport)
        self.ddbb.session.commit()
        self.assertEqual(22.5, sport.weight)
        
    def test_weight_should_not_accept_non_float_string(self):
        sport = Sport()
        sport.weight = "22.5kg"
        try:
            self.ddbb.session.add(sport)
            self.ddbb.session.flush()
        except StatementError:
            pass
        else:
            self.fail()
            
    def test_weight_should_not_accept_negative_value(self):
        if self.ddbb.engine.name == 'mysql':
            self.skipTest('Check constraints not available on Mysql')
        sport = Sport()
        sport.weight = -1
        try:
            self.ddbb.session.add(sport)
            self.ddbb.session.flush()
        except (IntegrityError, InterfaceError):
            pass
        else:
            self.fail()
            
    def test_weight_should_not_accept_none(self):
        sport = Sport()
        sport.weight = None
        try:
            self.ddbb.session.add(sport)
            self.ddbb.session.flush()
        except (IntegrityError, OperationalError):
            pass
        else:
            self.fail()
            
    def test_max_pace_should_default_to_none(self):
        sport = Sport()
        self.assertEqual(None, sport.max_pace)
        
    def test_max_pace_should_accept_integer(self):
        sport = Sport()
        sport.max_pace = 220
        self.ddbb.session.add(sport)
        self.ddbb.session.flush()
        self.assertEqual(220, sport.max_pace)
        
    def test_max_pace_should_accept_integer_string(self):
        sport = Sport()
        sport.max_pace = "220"
        self.ddbb.session.add(sport)
        self.ddbb.session.commit()
        self.assertEqual(220, sport.max_pace)
        
    def test_max_pace_should_not_accept_non_integer_string(self):
        sport = Sport()
        sport.max_pace = "225s"
        try:
            self.ddbb.session.add(sport)
            self.ddbb.session.flush()
        except(ValueError, StatementError):
            pass
        else:
            self.fail()
        
    def test_max_pace_should_take_floor_of_float(self):
        sport = Sport()
        sport.max_pace = 220.6
        self.ddbb.session.add(sport)
        self.ddbb.session.commit()
        sport = self.ddbb.session.query(Sport).filter(Sport.id == 1).one()
        self.assertEqual(220, sport.max_pace)

    def test_max_pace_should_not_accept_negative_value(self):
        if self.ddbb.engine.name == 'mysql':
            self.skipTest('Check constraints not available on Mysql')
        sport = Sport()
        sport.max_pace = -1
        try:
            self.ddbb.session.add(sport)
            self.ddbb.session.flush()
        except (IntegrityError, InterfaceError):
            pass
        else:
            self.fail()
            
    def test_max_pace_should_accept_none(self):
        sport = Sport()
        sport.max_pace = None
        self.assertEqual(None, sport.max_pace)
        
    def test_color_should_default_to_blue(self):
        sport = Sport()
        self.assertEqual(0x0000ff, sport.color.rgb_val)
        
    def test_color_should_not_accept_none(self):
        sport = Sport()
        sport.color = None
        try:
            self.ddbb.session.add(sport)
            self.ddbb.session.commit()
        except StatementError:
            pass
        else:
            self.fail()


class SportServiceTest(unittest.TestCase):
    
    def setUp(self):
        self.mock_ddbb = DDBB()
        self.mock_ddbb.connect()
        self.mock_ddbb.create_tables(add_default=False)
        self.sport_service = SportService(self.mock_ddbb)

    def tearDown(self):
        self.mock_ddbb.disconnect()
        self.mock_ddbb.drop_tables()
        
    def test_store_sport_should_insert_row_when_sport_has_no_id(self):
        sport = Sport()
        sport.name = u"Test name"
        sport = self.sport_service.store_sport(sport)
        self.assertEqual(1, sport.id)

    
    def test_store_sport_should_update_row_when_sport_has_id(self):
        sport = Sport()
        sport.name = u"Test name"
        sport = self.sport_service.store_sport(sport)
        sport.name = u"New name"
        self.sport_service.store_sport(sport)
        sport = self.sport_service.get_sport(1)
        self.assertEqual(sport.name, u"New name")
        
    def test_store_sport_should_return_stored_sport(self):
        sport = Sport()
        stored_sport = self.sport_service.store_sport(sport)
        self.assertEqual(1, stored_sport.id)
    
    def test_store_sport_should_error_when_new_sport_has_duplicate_name(self):
        sport1 = Sport()
        sport1.name = u"Test name"
        self.sport_service.store_sport(sport1)
        sport2 = Sport()
        sport2.name = u"Test name"
        try:
            self.sport_service.store_sport(sport2)
        except(SportServiceException):
            pass
        else:
            self.fail()

    def test_store_sport_should_error_when_existing_sport_has_duplicate_name(self):
        sport1 = Sport()
        sport1.name = u"Test name"
        self.sport_service.store_sport(sport1)
        sport2 = Sport()
        sport2.name = u"New name"
        self.sport_service.store_sport(sport2)
        sport1.name = u"New name"
        try:
            self.sport_service.store_sport(sport1)
        except(SportServiceException):
            pass
        else:
            self.fail()
    
    def test_get_sport_returns_none_for_nonexistant_sport(self):
        sport = self.sport_service.get_sport(1)
        self.assertEqual(None, sport)
        
    def test_get_sport_returns_sport_with_id(self):
        sport = Sport()
        sport.name = u"Test name"
        self.sport_service.store_sport(sport)
        sport = self.sport_service.get_sport(1)
        self.assertEqual(1, sport.id)
        
    def test_get_sport_raises_error_for_id_none(self):
        try:
            self.sport_service.get_sport(None)
        except(ValueError):
            pass
        else:
            self.fail()
        
    def test_get_sport_by_name_returns_none_for_nonexistant_sport(self):
        sport = self.sport_service.get_sport_by_name("no such sport")
        self.assertEqual(None, sport)
        
    def test_get_sport_by_name_returns_sport_with_name(self):
        sport1 = Sport()
        sport1.name = u"rugby"
        self.sport_service.store_sport(sport1)
        sport2 = self.sport_service.get_sport_by_name("rugby")
        self.assertEqual(u"rugby", sport2.name)
        
    def test_get_sport_by_name_raises_error_for_none_sport_name(self):
        try:
            self.sport_service.get_sport_by_name(None)
        except(ValueError):
            pass
        else:
            self.fail()
        
    def test_get_all_sports_should_return_all_sports_in_query_result(self):
        sport1 = Sport()
        sport1.name = u"Test name"
        self.sport_service.store_sport(sport1)
        sport2 = Sport()
        sport2.name = u"Test name 2"
        self.sport_service.store_sport(sport2)
        sports = self.sport_service.get_all_sports()
        self.assertEqual(2, len(sports))
        sport1 = sports[0]
        self.assertEqual(1, sport1.id)
        sport2 = sports[1]
        self.assertEqual(2, sport2.id)
    
    def test_get_all_sports_should_return_no_sports_when_query_result_empty(self):
        sports = self.sport_service.get_all_sports()
        self.assertEqual(0, len(sports))
        
    def test_remove_sport_should_error_when_sport_has_no_id(self):
        sport = Sport()
        try:
            self.sport_service.remove_sport(sport)
        except(SportServiceException):
            pass
        else:
            self.fail()
        
    def test_remove_sport_should_error_when_sport_has_unknown_id(self):
        sport = Sport()
        sport.id = 100
        try:
            self.sport_service.remove_sport(sport)
        except(SportServiceException):
            pass
        else:
            self.fail()
            
    def test_remove_sport_should_remove_associated_entries(self):
        sport = Sport()
        sport.name = u"Test name"
        sport = self.sport_service.store_sport(sport)
        self.sport_service.remove_sport(sport)
        result = self.sport_service.get_sport(1)
        self.assertEqual(result, None)
