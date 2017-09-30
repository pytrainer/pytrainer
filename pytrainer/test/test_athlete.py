#Copyright (C) Arto Jantunen <viiru@iki.fi>

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
from datetime import date
from mock import Mock

from pytrainer.lib.ddbb import DDBB
from pytrainer.profile import Profile
from pytrainer.athlete import Athlete

class AthleteTest(unittest.TestCase):

    def setUp(self):
        profile = Mock()
        profile.getValue = Mock(return_value='memory')
        self.ddbb = DDBB(profile)
        main = Mock()
        main.ddbb = self.ddbb
        main.profile = Profile()
        main.ddbb.connect()
        main.ddbb.create_tables(add_default=False)
        self.athlete = Athlete(parent=main)

    def tearDown(self):
        self.athlete = None
        self.ddbb.disconnect()
        self.ddbb = None

    def test_athlete_insert_and_get(self):
        data = {'date': date(2017, 4, 3), 'weight': 60.0, 'bodyfat': 20.0,
                'restinghr': 60, 'maxhr': 190, 'id_athletestat': 1}
        self.athlete.insert_athlete_stats(str(data['date']), data['weight'],
                                          data['bodyfat'], data['restinghr'],
                                          data['maxhr'])
        data2 = self.athlete.get_athlete_stats()
        self.assertEquals(data, data2[0])

    def test_athlete_update_and_get(self):
        data = {'date': date(2017, 4, 3), 'weight': 60.0, 'bodyfat': 20.0,
                'restinghr': 60, 'maxhr': 190, 'id_athletestat': 1}
        self.athlete.insert_athlete_stats(str(data['date']), data['weight'],
                                          data['bodyfat'], data['restinghr'],
                                          data['maxhr'])
        data['maxhr'] = 180
        data['bodyfat'] = 30.0
        self.athlete.update_athlete_stats(1, str(data['date']), data['weight'],
                                          data['bodyfat'], data['restinghr'],
                                          data['maxhr'])
        data2 = self.athlete.get_athlete_stats()
        self.assertEquals(data, data2[0])

    def test_athlete_delete_record(self):
        data = {'date': date(2017, 4, 3), 'weight': 60.0, 'bodyfat': 20.0,
                'restinghr': 60, 'maxhr': 190, 'id_athletestat': 1}
        self.athlete.insert_athlete_stats(str(data['date']), data['weight'],
                                          data['bodyfat'], data['restinghr'],
                                          data['maxhr'])
        self.athlete.delete_record(1)
        self.assertFalse(self.athlete.get_athlete_stats())
