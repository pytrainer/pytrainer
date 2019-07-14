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

from sqlalchemy.sql.expression import text
import logging

class _SportNormalizer(object):
    
    """A row from the sport DB table that can be "normalized" to have invalid
    values replaced with valid defaults."""
    
    def __init__(self, id, weight, color, met, max_pace):
        self._id = id
        self._weight = weight
        self._color =  color
        self._met = met
        self._max_pace = max_pace
        
    def normalize(self, migrate_engine):
        self._normalize_weight(migrate_engine)
        self._normalize_color(migrate_engine)
        self._normalize_met(migrate_engine)
        self._normalize_max_pace(migrate_engine)
            
    def _normalize_weight(self, migrate_engine):
        valid = True
        try:
            weight = float(self._weight)
            if weight < 0:
                valid = False
        except:
            valid = False
        if not valid:
            logging.debug("Sport with id '%s' has invalid weight: '%s'. Replacing with default.", self._id, self._weight)
            migrate_engine.execute(text("update sports set weight=:weight where id_sports=:id"), id=self._id, weight=0.0)
            
    def _normalize_color(self, migrate_engine):
        try:
            # colors that do not have exactly 6 hexadecimal digits should also
            # be invalid, but we do not expect such invalid values to exist.
            int(self._color, 16)
        except:
            logging.debug("Sport with id '%s' has invalid color: '%s'. Replacing with default.", self._id, self._color)
            migrate_engine.execute(text("update sports set color=:color where id_sports=:id"), id=self._id, color="0000ff")
            
    def _normalize_met(self, migrate_engine):
        valid = True
        if self._met is not None:
            try:
                met = float(self._met)
                if met < 0:
                    valid = False
            except:
                valid = False
        if not valid:
            logging.debug("Sport with id '%s' has invalid MET: '%s'. Replacing with default.", self._id, self._met)
            migrate_engine.execute(text("update sports set met=:met where id_sports=:id"), id=self._id, met=None)
            
    def _normalize_max_pace(self, migrate_engine):
        valid = True
        if self._max_pace is not None:
            try:
                max_pace = int(self._max_pace)
                if max_pace <= 0:
                    valid = False
            except:
                valid = False
        if not valid:
            logging.debug("Sport with id '%s' has invalid max pace: '%s'. Replacing with default.", self._id, self._max_pace)
            migrate_engine.execute(text("update sports set max_pace=:max_pace where id_sports=:id"), id=self._id, max_pace=None)

def upgrade(migrate_engine):
    sport_rows = migrate_engine.execute("select id_sports, weight, color, met, max_pace from sports")
    sport_normalizers = []
    for (id, weight, color, met, max_pace) in sport_rows:
        sport_normalizers.append(_SportNormalizer(id, weight, color, met, max_pace))
    for sport_normalizer in sport_normalizers:
        sport_normalizer.normalize(migrate_engine)
