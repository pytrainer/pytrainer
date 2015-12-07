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

import logging

class Equipment(object):
   
   """An equipment item that can be used during an activity, such as a pair of running shoes."""
   
   def __init__(self):
       self._id = None
       self.description = u""
       self.active = True
       self.life_expectancy = 0
       self.prior_usage = 0
       self.notes = u""
       
   def _get_id(self):
       return self._id
   
   def _set_id(self, id):
       self._id = int(id)
       
   id = property(_get_id, _set_id)
       
   def _get_description(self):
       return self._description
   
   def _set_description(self, description):
       if not isinstance(description, unicode):
           raise TypeError("Description must be unicode string, not {0}.".format(type(description).__name__))
       self._description = description
       
   description = property(_get_description, _set_description)
       
   def _get_active(self):
       return self._active
   
   def _set_active(self, active):
       if not isinstance(active, bool):
           raise TypeError("Active must be boolean, not {0}.".format(type(active).__name__))
       self._active = active
       
   active = property(_get_active, _set_active)
       
   def _get_life_expectancy(self):
       return self._life_expectancy
   
   def _set_life_expectancy(self, life_expectancy):
       self._life_expectancy = int(life_expectancy)
       
   life_expectancy = property(_get_life_expectancy, _set_life_expectancy)
       
   def _get_prior_usage(self):
       return self._prior_usage
   
   def _set_prior_usage(self, prior_usage):
       self._prior_usage = int(prior_usage)
       
   prior_usage = property(_get_prior_usage, _set_prior_usage)
   
   def _get_notes(self):
       return self._notes
   
   def _set_notes(self, notes):
       if not isinstance(notes, unicode):
           raise TypeError("Notes must be unicode string, not {0}.".format(type(notes).__name__))
       self._notes = notes
       
   notes = property(_get_notes, _set_notes)
       
   def __eq__(self, o):
       if isinstance(o, Equipment):
           if self.id is not None and o.id is not None:
               return self.id == o.id
       return False
       
   def __hash__(self):
       if self.id is not None:
           return self.id
       else:
           return object.__hash__(self)

_TABLE_NAME = "equipment"
   
_UPDATE_COLUMNS = "description,active,life_expectancy,prior_usage,notes"

_ALL_COLUMNS = "id," + _UPDATE_COLUMNS
       
def _create_row(equipment):
   return [equipment.description,
           1 if equipment.active else 0,
           equipment.life_expectancy,
           equipment.prior_usage,
           equipment.notes]

class EquipmentServiceException(Exception):
   
   def __init__(self, value):
       self.value = value
   
   def __str__(self):
       return repr(self.value)
       
class EquipmentService(object):
   
   """Provides access to stored equipment items."""
   
   def __init__(self, ddbb):
       self._ddbb = ddbb
       
   def get_all_equipment(self):
       """Get all equipment items."""
       return self._get_equipment(None)
   
   def get_active_equipment(self):
       """Get all the active equipment items."""
       return self._get_equipment("active = 1")
   
   def _get_equipment(self, condition):
       logging.debug("Retrieving all equipment (condition: '{0}').".format(condition))
       resultSet = self._ddbb.select(_TABLE_NAME, _ALL_COLUMNS, condition)
       equipmentList = []
       for result in resultSet:
           equipmentList.append(self._create_equipment_item(result))
       return equipmentList
   
   def get_equipment_item(self, item_id):
       """Get an individual equipment item by id.
       
       If no item with the given id exists then None is returned.
       """
       resultSet = self._ddbb.select(_TABLE_NAME, _ALL_COLUMNS, "id = {0}".format(item_id))
       if len(resultSet) == 0:
           return None
       else:
           return self._create_equipment_item(resultSet[0])
       
   def _create_equipment_item(self, row):
       equipment = Equipment()
       (id, description, active, life_expectancy, prior_usage, notes) = row
       equipment.id = id
       equipment.description = unicode(description)
       equipment.active = bool(active)
       equipment.life_expectancy = life_expectancy
       equipment.prior_usage = prior_usage
       equipment.notes = unicode(notes)
       return equipment
       
   def store_equipment(self, equipment):
       """Store a new or update an existing equipment item.
       
       The stored object is returned."""
       logging.debug("Storing equipment item.")
       item_id = None
       if equipment.id != None:
           item_id = self._update_equipment(equipment)
       else:
           item_id = self._store_new_equipment(equipment)
       return self.get_equipment_item(item_id)
   
   def _update_equipment(self, equipment):
       logging.debug("Updating existing equipment item.")
       self._assert_exists(equipment)
       self._assert_unique(equipment)
       self._ddbb.update(_TABLE_NAME, _UPDATE_COLUMNS, _create_row(equipment), "id = {0}".format(equipment.id))
       return equipment.id
   
   def _assert_exists(self, equipment):
       if self.get_equipment_item(equipment.id) == None:
           raise EquipmentServiceException("No equipment item exists with id '{0}'".format(equipment.id))
       logging.debug("Asserted item exists with id: '{0}'.".format(equipment.id))
   
   def _store_new_equipment(self, equipment):
       logging.debug("Storing new equipment item.")
       self._assert_unique(equipment)
       self._ddbb.insert(_TABLE_NAME, _UPDATE_COLUMNS, _create_row(equipment))
       return self._ddbb.select(_TABLE_NAME, "id", "description = \"{0}\"".format(equipment.description))[0][0]
       
   def _assert_unique(self, equipment):
       result = self._ddbb.select(_TABLE_NAME, "id", "description = \"{0}\"".format(equipment.description))
       if len(result) > 0:
           id = result[0][0]
           if id != equipment.id:
               raise EquipmentServiceException("An equipment item already exists with description '{0}'".format(equipment.description))
       logging.debug("Asserted description is unique: '{0}'.".format(equipment.description))
   
   def remove_equipment(self, equipment):
       """Remove an existing equipment item."""
       logging.debug("Deleting equipment item with id: '{0}'".format(equipment.id))
       self._ddbb.delete("record_equipment", "equipment_id=\"{0}\"".format(equipment.id))
       self._ddbb.delete(_TABLE_NAME, "id=\"{0}\"".format(equipment.id))
   
   def get_equipment_usage(self, equipment):
       """Get the total use of the given equipment."""
       result = self._ddbb.select("records inner join record_equipment "
                         "on records.id_record = record_equipment.record_id",
                         "sum(distance)",
                         "record_equipment.equipment_id = {0}".format(equipment.id))
       usage = result[0][0]
       return (0 if usage == None else usage) + equipment.prior_usage
