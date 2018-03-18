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
import mock
from pytrainer.core.equipment import Equipment, EquipmentService,\
    EquipmentServiceException
from pytrainer.lib.ddbb import DDBB, DeclarativeBase
from sqlalchemy.exc import StatementError, IntegrityError, ProgrammingError, OperationalError, DataError

class EquipmentTest(unittest.TestCase):

    def setUp(self):
        self.ddbb = DDBB()
        self.ddbb.connect()
        self.ddbb.create_tables()

    def tearDown(self):
        self.ddbb.disconnect()
        self.ddbb.drop_tables()
    
    def test_id_defaults_to_none(self):
        equipment = Equipment()
        self.assertEqual(None, equipment.id)
            
    def test_id_set_to_integer(self):
        equipment = Equipment()
        equipment.id = 2
        self.assertEquals(2, equipment.id)
            
    def test_id_set_to_numeric_string(self):
        equipment = Equipment()
        equipment.id = "3"
        self.ddbb.session.add(equipment)
        self.ddbb.session.commit()
        self.assertEquals(3, equipment.id)

    def test_id_set_to_non_numeric_string(self):
        if self.ddbb.engine.name == 'mysql':
            self.skipTest('Not supported on Mysql 5.6')
        equipment = Equipment()
        equipment.id = "test"
        try:
            self.ddbb.session.add(equipment)
            self.ddbb.session.flush()
        except (IntegrityError, OperationalError, DataError):
            pass
        else:
            self.fail("Should not be able to set equipment id to non numeric value.")
            
    def test_description_defaults_to_empty_string(self):
        equipment = Equipment()
        self.assertEquals(u"", equipment.description)

    @unittest.skipIf(sys.version_info > (3, 0), "All strings are unicode in Python 3")
    def test_description_set_to_non_unicode_string(self):
        if self.ddbb.engine.name == 'mysql':
            self.skipTest('Not supported on Mysql 5.6')
        equipment = Equipment()
        equipment.description = "100$ Shoes" + chr(255)
        try:
            self.ddbb.session.add(equipment)
            self.ddbb.session.flush()
        except (ProgrammingError, DataError, OperationalError):
            pass
        else:
            self.fail("Should not be able to set description to non unicode string value.")
            
    def test_description_set_to_unicode_string(self):
        equipment = Equipment()
        equipment.description = u"Zapatos de €100"
        self.assertEquals(u"Zapatos de €100", equipment.description)
        
    def test_description_set_to_non_string(self):
        equipment = Equipment()
        equipment.description = 42
        self.ddbb.session.add(equipment)
        self.ddbb.session.commit()
        self.assertEquals(u"42", equipment.description)
            
    def test_active_defaults_to_true(self):
        equipment = Equipment()
        self.assertTrue(equipment.active)
            
    def test_active_set_to_boolean(self):
        equipment = Equipment()
        equipment.active = False
        self.assertFalse(equipment.active)
            
    def test_active_set_to_non_boolean(self):
        equipment = Equipment()
        equipment.active = "test"
        self.ddbb.session.add(equipment)
        try:
            self.ddbb.session.commit()
            self.assertTrue(equipment.active)
        except StatementError:
            pass

    def test_life_expectancy_defaults_to_zero(self):
        equipment = Equipment()
        self.assertEqual(0, equipment.life_expectancy)
            
    def test_life_expectancy_set_to_integer(self):
        equipment = Equipment()
        equipment.life_expectancy = 2
        self.assertEquals(2, equipment.life_expectancy)
            
    def test_life_expectancy_set_to_numeric_string(self):
        equipment = Equipment()
        equipment.life_expectancy = "3"
        self.ddbb.session.add(equipment)
        self.ddbb.session.commit()
        self.assertEquals(3, equipment.life_expectancy)

    def test_life_expectancy_set_to_non_numeric_string(self):
        equipment = Equipment()
        equipment.life_expectancy = "test"
        try:
            self.ddbb.session.add(equipment)
            self.ddbb.session.flush()
        except StatementError:
            pass
        else:
            self.fail("Should not be able to set life expectancy to non numeric value.")
    
    def test_prior_usage_defaults_to_zero(self):
        equipment = Equipment()
        self.assertEqual(0, equipment.prior_usage)
            
    def test_prior_usage_set_to_integer(self):
        equipment = Equipment()
        equipment.prior_usage = 2
        self.assertEquals(2, equipment.prior_usage)
            
    def test_prior_usage_set_to_numeric_string(self):
        equipment = Equipment()
        equipment.prior_usage = "3"
        self.ddbb.session.add(equipment)
        self.ddbb.session.commit()
        self.assertEquals(3, equipment.prior_usage)

    def test_prior_usage_set_to_non_numeric_string(self):
        equipment = Equipment()
        equipment.prior_usage = "test"
        try:
            self.ddbb.session.add(equipment)
            self.ddbb.session.flush()
        except StatementError:
            pass
        else:
            self.fail("Should not be able to set life expectancy to non numeric value.")
            
    def test_notes_defaults_to_empty_string(self):
        equipment = Equipment()
        self.assertEquals(u"", equipment.notes)

    @unittest.skipIf(sys.version_info > (3, 0), "All strings are unicode in Python 3")
    def test_notes_set_to_string(self):
        if self.ddbb.engine.name == 'mysql':
            self.skipTest('Not supported on Mysql 5.6')
        equipment = Equipment()
        equipment.notes = "100$ Shoes" + chr(255)
        try:
            self.ddbb.session.add(equipment)
            self.ddbb.session.flush()
        except (ProgrammingError, DataError, OperationalError):
            pass
        else:
            self.fail("Should not be able to set notes to non-unicode string value.")
            
    def test_notes_set_to_unicode_string(self):
        equipment = Equipment()
        equipment.notes = u"Zapatos de €100."
        self.assertEquals(u"Zapatos de €100.", equipment.notes)
        
    def test_notes_set_to_non_string(self):
        equipment = Equipment()
        equipment.notes = 42
        self.ddbb.session.add(equipment)
        self.ddbb.session.commit()
        self.assertEquals(u"42", equipment.notes)
            
    def test_equals_new_instances(self):
        equipment1 = Equipment()
        equipment2 = Equipment()
        self.assertNotEqual(equipment1, equipment2, "")
            
    def test_equals_instances_with_same_id(self):
        equipment1 = Equipment()
        equipment1.id = 1
        equipment2 = Equipment()
        equipment2.id = 1
        self.assertEqual(equipment1, equipment2, "Equipment instances with same id should be equal.")
            
    def test_equals_instances_with_different_ids(self):
        equipment1 = Equipment()
        equipment1.id = 1
        equipment2 = Equipment()
        equipment2.id = 2
        self.assertNotEqual(equipment1, equipment2, "Equipment instances with different ids should not be equal.")

class EquipmentServiceTest(unittest.TestCase):
    
    def setUp(self):
        self.mock_ddbb = DDBB()
        self.mock_ddbb.connect()
        self.mock_ddbb.create_tables()
        self.equipment_service = EquipmentService(self.mock_ddbb)
        self.equipment_table = DeclarativeBase.metadata.tables['equipment']
        
    def tearDown(self):
        self.mock_ddbb.disconnect()
        self.mock_ddbb.drop_tables()
    
    def test_get_equipment_item(self):
        self.mock_ddbb.session.execute(self.equipment_table.insert(),
                                           {"life_expectancy": 500,
                                                "notes": u"Test notes.",
                                           "description": u"Test Description",
                                           "prior_usage": 200, "active": True})
        item = self.equipment_service.get_equipment_item(1)
        self.assertEquals(1, item.id)
        self.assertEquals("Test Description", item.description)
        self.assertTrue(item.active)
        self.assertEquals(500, item.life_expectancy)
        self.assertEquals(200, item.prior_usage)
        self.assertEquals("Test notes.", item.notes)
    
    def test_get_equipment_item_non_unicode(self):
        self.mock_ddbb.session.execute(self.equipment_table.insert(),
                                           {"life_expectancy": 500,
                                                "notes": u"Test notes.",
                                           "description": u"Test Description",
                                           "prior_usage": 200, "active": True})
        item = self.equipment_service.get_equipment_item(1)
        self.assertEquals("Test Description", item.description)
        self.assertEquals("Test notes.", item.notes)
    
    def test_get_equipment_item_non_existant(self):
        item = self.equipment_service.get_equipment_item(1)
        self.assertEquals(None, item)
        
    def test_get_all_equipment(self):
        self.mock_ddbb.session.execute(self.equipment_table.insert(),
                                           {"life_expectancy": 500,
                                                "notes": u"Test notes 1.",
                                           "description": u"Test item 1",
                                           "prior_usage": 200, "active": True})
        self.mock_ddbb.session.execute(self.equipment_table.insert(),
                                           {"life_expectancy": 600,
                                                "notes": u"Test notes 2.",
                                           "description": u"Test item 2",
                                           "prior_usage": 300, "active": False})
        items = self.equipment_service.get_all_equipment()
        item = items[0]
        self.assertEquals(1, item.id)
        self.assertEquals("Test item 1", item.description)
        self.assertTrue(item.active)
        self.assertEquals(500, item.life_expectancy)
        self.assertEquals(200, item.prior_usage)
        self.assertEquals("Test notes 1.", item.notes)
        item = items[1]
        self.assertEquals(2, item.id)
        self.assertEquals("Test item 2", item.description)
        self.assertFalse(item.active)
        self.assertEquals(600, item.life_expectancy)
        self.assertEquals(300, item.prior_usage)
        self.assertEquals("Test notes 2.", item.notes)
        
    def test_get_all_equipment_non_existant(self):
        items = self.equipment_service.get_all_equipment()
        self.assertEquals([], items)
        
    def test_get_active_equipment(self):
        self.mock_ddbb.session.execute(self.equipment_table.insert(),
                                           {"life_expectancy": 500,
                                                "notes": u"Test notes 1.",
                                           "description": u"Test item 1",
                                           "prior_usage": 200, "active": True})
        self.mock_ddbb.session.execute(self.equipment_table.insert(),
                                           {"life_expectancy": 600,
                                                "notes": u"Test notes 2.",
                                           "description": u"Test item 2",
                                           "prior_usage": 300, "active": True})
        items = self.equipment_service.get_active_equipment()
        item = items[0]
        self.assertEquals(1, item.id)
        self.assertEquals("Test item 1", item.description)
        self.assertTrue(item.active)
        self.assertEquals(500, item.life_expectancy)
        self.assertEquals(200, item.prior_usage)
        self.assertEquals("Test notes 1.", item.notes)
        item = items[1]
        self.assertEquals(2, item.id)
        self.assertEquals("Test item 2", item.description)
        self.assertTrue(item.active)
        self.assertEquals(600, item.life_expectancy)
        self.assertEquals(300, item.prior_usage)
        self.assertEquals("Test notes 2.", item.notes)
        
    def test_get_active_equipment_non_existant(self):
        items = self.equipment_service.get_active_equipment()
        self.assertEquals([], items)
        
    def test_store_equipment(self):
        equipment = Equipment()
        equipment.description = u"test description"
        stored_equipment = self.equipment_service.store_equipment(equipment)
        self.assertEquals(1, stored_equipment.id)
        
    def test_store_equipment_duplicate_description(self):
        self.mock_ddbb.session.execute(self.equipment_table.insert(),
                                           {"life_expectancy": 500,
                                                "notes": u"Test notes.",
                                           "description": u"test item",
                                           "prior_usage": 200, "active": True})
        equipment = Equipment()
        equipment.description = u"test item"
        try:
            self.equipment_service.store_equipment(equipment)
            self.fail("Should not be able to store new item with non-unique description.")
        except(EquipmentServiceException):
            pass
        
    def test_update_equipment(self):
        self.mock_ddbb.session.execute(self.equipment_table.insert(),
                                           {"life_expectancy": 500,
                                                "notes": u"Test notes.",
                                           "description": u"old description",
                                           "prior_usage": 200, "active": True})
        equipment = self.equipment_service.get_equipment_item(1)
        equipment.description = u"new description"
        self.equipment_service.store_equipment(equipment)
        equipment = self.equipment_service.get_equipment_item(1)
        self.assertEquals("new description", equipment.description)
        
    def test_update_equipment_duplicate_description(self):
        self.mock_ddbb.session.execute(self.equipment_table.insert(),
                                           {"life_expectancy": 500,
                                                "notes": u"Test notes.",
                                           "description": u"test item",
                                           "prior_usage": 200, "active": True})
        equipment = Equipment()
        equipment.id = 2
        equipment.description = u"test item"
        try:
            self.equipment_service.store_equipment(equipment)
            self.fail("Should not be able to change item description to non-unique value.")
        except(EquipmentServiceException):
            pass
        
    def test_get_equipment_usage(self):
        self.mock_ddbb.session.execute(self.equipment_table.insert(),
                                           {"life_expectancy": 500,
                                                "notes": u"Test notes.",
                                           "description": u"test item",
                                           "prior_usage": 0, "active": True})
        self.mock_ddbb.session.execute("insert into records (distance,sport) values (250,1)")
        self.mock_ddbb.session.execute("insert into record_equipment (record_id,equipment_id) values (1,1)")
        equipment = self.equipment_service.get_equipment_item(1)
        usage = self.equipment_service.get_equipment_usage(equipment)
        self.assertEquals(250, usage)
        
    def test_get_equipment_usage_none(self):
        self.mock_ddbb.session.execute(self.equipment_table.insert(),
                                           {"life_expectancy": 500,
                                                "notes": u"Test notes.",
                                           "description": u"test item",
                                           "prior_usage": 0, "active": True})
        equipment = self.equipment_service.get_equipment_item(1)
        usage = self.equipment_service.get_equipment_usage(equipment)
        self.assertEquals(0, usage)

    def test_get_equipment_prior_usage(self):
        equipment = Equipment()
        equipment.id = 1
        equipment.prior_usage = 250
        usage = self.equipment_service.get_equipment_usage(equipment)
        self.assertEquals(250, usage)

    def test_get_equipment_prior_usage(self):
        equipment = Equipment()
        equipment.id = 1
        equipment.prior_usage = 250
        usage = self.equipment_service.get_equipment_usage(equipment)
        self.assertEquals(250, usage)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
