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

import unittest
import sqlalchemy
import pytrainer.upgrade.versions.version014 as version014

class UpgradeTest(unittest.TestCase):
    
    def setUp(self):
        self._engine = sqlalchemy.create_engine("sqlite:///:memory:")
        self._metadata = sqlalchemy.MetaData()
        self._metadata.bind = self._engine
        self._sports_table = sqlalchemy.Table("sports", self._metadata,
            sqlalchemy.Column("id_sports", sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column("name", sqlalchemy.String(100)),
            sqlalchemy.Column("weight", sqlalchemy.Float),
            sqlalchemy.Column("color", sqlalchemy.String(6)),
            sqlalchemy.Column("met", sqlalchemy.Float),
            sqlalchemy.Column("max_pace", sqlalchemy.Integer)
        )
        self._metadata.drop_all()
        self._metadata.create_all()
        
    def upgradeAndAssert(self, original, expected):
        self._engine.execute(sqlalchemy.text("insert into sports (id_sports, name, weight, color, met, max_pace)"
                                             " values (:id, :name, :weight, :color, :met, :max_pace)"),
                                           id= 1,
                                           name= "Test Sport",
                                           weight= original["weight"],
                                           color= original["color"],
                                           met= original["met"],
                                           max_pace= original["max_pace"])
        version014.upgrade(self._engine)
        result = self._engine.execute(self._sports_table.select(self._sports_table.c.id_sports==1))
        (_, _, weight, color, met, max_pace) = result.fetchone()
        result.close()
        self.assertEqual(expected["weight"], weight)
        self.assertEqual(expected["color"], color)
        self.assertEqual(expected["met"], met)
        self.assertEqual(expected["max_pace"], max_pace)
        
    def testUpgradeFromNullValues(self):
        original = { "weight": None, "color": None, "met": None, "max_pace": None }
        expected = { "weight": 0.0, "color": "0000ff", "met": None, "max_pace": None }
        self.upgradeAndAssert(original, expected)
        
    def testUpgradeFromZeroValues(self):
        original = { "weight": 0, "color": 0, "met": 0, "max_pace": 0 }
        expected = { "weight": 0.0, "color": "0", "met": 0, "max_pace": None }
        self.upgradeAndAssert(original, expected)
        
    def testUpgradeFromEmptyValues(self):
        original = { "weight": "", "color": "", "met": "", "max_pace": "" }
        expected = { "weight": 0.0, "color": "0000ff", "met": None, "max_pace": None }
        self.upgradeAndAssert(original, expected)
        
    def testUpgradeFromNegativeValues(self):
        original = { "weight": -1, "color": -1, "met": -1, "max_pace": -1 } 
        expected = { "weight": 0.0, "color": "-1", "met": None, "max_pace": None }
        self.upgradeAndAssert(original, expected)
        
    def testUpgradeFromValidValues(self):
        original = { "weight": 3.4, "color": "abc123", "met": 45.6, "max_pace": 123 }
        expected = { "weight": 3.4, "color": "abc123", "met": 45.6, "max_pace": 123 }
        self.upgradeAndAssert(original, expected)
