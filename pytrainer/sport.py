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

from pytrainer.lib.color import Color, color_from_hex_string
import logging

class Sport(object):
    
    """A type of exercise. For example: "running" or "cycling"."""
    
    def __init__(self):
        self._id = None
        self.name = u""
        self.weight = 0.0
        self.met = None
        self.max_pace = None
        self.color = Color(0x0000ff)
       
    def _get_id(self):
        return self._id
    
    def _set_id(self, id):
        self._id = int(id)
    
    id = property(_get_id, _set_id)
       
    def _get_name(self):
        return self._name
    
    def _set_name(self, name):
        if not isinstance(name, unicode):
            raise TypeError("Name must be unicode string, not {0}.".format(type(name).__name__))
        self._name = name
    
    name = property(_get_name, _set_name)
       
    def _get_weight(self):
        return self._weight
    
    def _set_weight(self, weight):
        weight_float = float(weight)
        if weight_float < 0:
            raise ValueError("Weight must not be negative.")
        self._weight = weight_float
    
    weight = property(_get_weight, _set_weight)
       
    def _get_met(self):
        return self._met
    
    def _set_met(self, met):
        met_float = float(met) if met is not None else None
        if met_float is not None and met_float < 0:
            raise ValueError("MET must not be negative.")
        self._met = met_float
    
    met = property(_get_met, _set_met)
       
    def _get_max_pace(self):
        return self._max_pace
    
    def _set_max_pace(self, max_pace):
        max_pace_int = int(max_pace) if max_pace is not None else None
        if max_pace_int is not None and max_pace_int < 0:
            raise ValueError("Max pace must not be negative.")
        self._max_pace = max_pace_int
    
    max_pace = property(_get_max_pace, _set_max_pace)
    
    def _get_color(self):
        return self._color
    
    def _set_color(self, color):
        if color is None:
            raise ValueError("Color must be valued.")
        self._color = color
        
    color = property(_get_color, _set_color)

class SportServiceException(Exception):
    
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)

_TABLE = "sports"

_ID_COLUMN = "id_sports"

_NAME_COLUMN = "name"

_UPDATE_COLUMNS = _NAME_COLUMN + ",weight,met,max_pace,color"

_SELECT_COLUMNS = _ID_COLUMN + "," + _UPDATE_COLUMNS
    
class SportService(object):
    
    """Provides access to stored sports."""
    
    def __init__(self, ddbb):
        self._ddbb = ddbb
        
    def _create_sport(self, row):
        sport = Sport()
        sport.id = row[0]
        sport.name = unicode(row[1])
        sport.weight = row[2]
        sport.met = row[3]
        sport.max_pace = row[4]
        sport.color =  color_from_hex_string(row[5])
        return sport
    
    def _create_row(self, sport):
        return [sport.name,
                sport.weight,
                sport.met,
                sport.max_pace,
                sport.color.to_hex_string()]
        
    def _create_id_where_clause(self, sport_id):
        return _ID_COLUMN + "=" + str(sport_id)
    
    def _create_name_where_clause(self, sport_name):
        return _NAME_COLUMN + "=\"{0}\"".format(sport_name)
    
    def get_sport(self, sport_id):
        """Get the sport with the specified id.

        If no sport with the given id exists then None is returned."""
        resultSet = self._ddbb.select(_TABLE, _SELECT_COLUMNS, self._create_id_where_clause(sport_id))
        if len(resultSet) == 0:
            return None
        else:
            return self._create_sport(resultSet[0])
        
    def get_sport_by_name(self, name):
        """Get the sport with the specified name.

        If no sport with the given name exists then None is returned."""
        sport_id = self._get_sport_id_from_name(name)
        return self.get_sport(sport_id)
        
    def _get_sport_id_from_name(self, name):
        result_set = self._ddbb.select(_TABLE, _ID_COLUMN, self._create_name_where_clause(name))
        if len(result_set) > 0:
            return result_set[0][0]
        return None
    
    def get_all_sports(self):
        """Get all stored sports."""
        result_set = self._ddbb.select(_TABLE, _SELECT_COLUMNS)
        logging.debug("Retrieved all sports ({0} results).".format(len(result_set)))
        sports = []
        for row in result_set:
            sport = self._create_sport(row)
            sports.append(sport)
        return sports
    
    def store_sport(self, sport):
        """Store a new or update an existing sport.
       
       The stored object is returned."""
        if (sport.id is None):
            sport_id = self._store_new_sport(sport)
        else:
            sport_id = self._update_existing_sport(sport)
        return self.get_sport(sport_id)
    
    def _store_new_sport(self, sport):
        self._assert_unique(sport)
        self._ddbb.insert(_TABLE, _UPDATE_COLUMNS, self._create_row(sport))
        logging.debug("Stored new sport: '{0}'.".format(sport.name))
        return self._get_sport_id_from_name(sport.name)
    
    def _update_existing_sport(self, sport):
        self._assert_exists(sport)
        self._assert_unique(sport)
        self._ddbb.update(_TABLE, _UPDATE_COLUMNS, self._create_row(sport), self._create_id_where_clause(sport.id))
        logging.debug("Updated sport: '{0}'.".format(sport.name))
        return sport.id
        
    def _assert_unique(self, sport):
        id = self._get_sport_id_from_name(sport.name)
        if id is not None and id != sport.id:
            raise SportServiceException("A sport already exists with name '{0}'".format(sport.name))
        logging.debug("Asserted sport name is unique: '{0}'.".format(sport.name))
        
    def _assert_exists(self, sport):
        result_set = self._ddbb.select(_TABLE, _ID_COLUMN, self._create_id_where_clause(sport.id))
        if (result_set == []):
            raise SportServiceException("Sport does not exist with id: '{0}'.".format(sport.id))
        logging.debug("Asserted sport exists with id: '{0}'.".format(sport.id))
        
    def remove_sport(self, sport):
        """Delete a stored sport.
        
        All records associated with the sport will also be deleted."""
        if (sport.id is None):
            raise SportServiceException("Cannot remove sport which has not been stored: '{0}'.".format(sport.name))
        self._assert_exists(sport)
        self._ddbb.delete("records", "sport=" + str(sport.id))
        self._ddbb.delete(_TABLE, self._create_id_where_clause(sport.id))
        logging.debug("Deleted sport: '{0}'.".format(sport.name))
