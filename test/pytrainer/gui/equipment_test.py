# -*- coding: utf-8 -*-
from unittest import TestCase
from mock import Mock
from pytrainer.equipment import Equipment, EquipmentService
from pytrainer.gui.equipment import EquipmentStore

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

class EquipmentStoreTest(TestCase):
    
    def setUp(self):
        self.mock_equipment_service = Mock(spec=EquipmentService)
        self.mock_equipment_service.get_equipment_usage.return_value = 0
    
    def tearDown(self):
        pass
        
    def test_get_item_id(self):
        equipment = Equipment()
        equipment.id = 1
        self.mock_equipment_service.get_all_equipment.return_value = [equipment]
        equipment_store = EquipmentStore(self.mock_equipment_service)
        iter = equipment_store.get_iter_first()
        self.assertEquals(1, equipment_store.get_value(iter, 0))
        
    def test_get_item_description(self):
        equipment = Equipment()
        equipment.id = 1
        equipment.description = u"item description"
        self.mock_equipment_service.get_all_equipment.return_value = [equipment]
        equipment_store = EquipmentStore(self.mock_equipment_service)
        iter = equipment_store.get_iter_first()
        self.assertEquals("item description", equipment_store.get_value(iter, 1))
        
    def test_get_item_usage_percent(self):
        equipment = Equipment()
        equipment.id = 1
        equipment.life_expectancy = 200
        self.mock_equipment_service.get_all_equipment.return_value = [equipment]
        self.mock_equipment_service.get_equipment_usage.return_value = 100
        equipment_store = EquipmentStore(self.mock_equipment_service)
        iter = equipment_store.get_iter_first()
        self.assertEquals(50, equipment_store.get_value(iter, 2))
        
    def test_get_item_usage_percent_prior_usage(self):
        equipment = Equipment()
        equipment.id = 1
        equipment.life_expectancy = 200
        equipment.prior_usage = 50
        self.mock_equipment_service.get_all_equipment.return_value = [equipment]
        self.mock_equipment_service.get_equipment_usage.return_value = 100
        equipment_store = EquipmentStore(self.mock_equipment_service)
        iter = equipment_store.get_iter_first()
        self.assertEquals(75, equipment_store.get_value(iter, 2))
        
    def test_get_item_usage_percent_zero_usage(self):
        equipment = Equipment()
        equipment.id = 1
        equipment.life_expectancy = 200
        self.mock_equipment_service.get_all_equipment.return_value = [equipment]
        self.mock_equipment_service.get_equipment_usage.return_value = 0
        equipment_store = EquipmentStore(self.mock_equipment_service)
        iter = equipment_store.get_iter_first()
        self.assertEquals(0, equipment_store.get_value(iter, 2))
        
    def test_get_item_usage_text(self):
        equipment = Equipment()
        equipment.id = 1
        equipment.life_expectancy = 200
        self.mock_equipment_service.get_all_equipment.return_value = [equipment]
        self.mock_equipment_service.get_equipment_usage.return_value = 100
        equipment_store = EquipmentStore(self.mock_equipment_service)
        iter = equipment_store.get_iter_first()
        self.assertEquals("100 / 200", equipment_store.get_value(iter, 3))
        
    def test_get_item_usage_text_rounded(self):
        equipment = Equipment()
        equipment.id = 1
        equipment.life_expectancy = 200
        self.mock_equipment_service.get_all_equipment.return_value = [equipment]
        self.mock_equipment_service.get_equipment_usage.return_value = 100.5
        equipment_store = EquipmentStore(self.mock_equipment_service)
        iter = equipment_store.get_iter_first()
        self.assertEquals("101 / 200", equipment_store.get_value(iter, 3))
        
    def test_get_item_usage_text_prior_usage(self):
        equipment = Equipment()
        equipment.id = 1
        equipment.life_expectancy = 200
        equipment.prior_usage = 50
        self.mock_equipment_service.get_all_equipment.return_value = [equipment]
        self.mock_equipment_service.get_equipment_usage.return_value = 100
        equipment_store = EquipmentStore(self.mock_equipment_service)
        iter = equipment_store.get_iter_first()
        self.assertEquals("150 / 200", equipment_store.get_value(iter, 3))
        
    def test_get_item_usage_text_zero_usage(self):
        equipment = Equipment()
        equipment.id = 1
        equipment.life_expectancy = 200
        self.mock_equipment_service.get_all_equipment.return_value = [equipment]
        self.mock_equipment_service.get_equipment_usage.return_value = 0
        equipment_store = EquipmentStore(self.mock_equipment_service)
        iter = equipment_store.get_iter_first()
        self.assertEquals("0 / 200", equipment_store.get_value(iter, 3))
        
    def test_get_item_active(self):
        equipment = Equipment()
        equipment.id = 1
        equipment.active = False
        self.mock_equipment_service.get_all_equipment.return_value = [equipment]
        equipment_store = EquipmentStore(self.mock_equipment_service)
        iter = equipment_store.get_iter_first()
        self.assertFalse(equipment_store.get_value(iter, 4))
    
    def test_multiple_equipment_items(self):
        equipment1 = Equipment()
        equipment1.id = 1
        equipment2 = Equipment()
        equipment2.id = 2
        self.mock_equipment_service.get_all_equipment.return_value = [equipment1, equipment2]
        equipment_store = EquipmentStore(self.mock_equipment_service)
        iter = equipment_store.get_iter_first()
        iter = equipment_store.iter_next(iter)
        self.assertEquals(2, equipment_store.get_value(iter, 0))
        

