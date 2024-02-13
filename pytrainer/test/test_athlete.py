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

from datetime import date
from unittest.mock import Mock

from pytrainer.profile import Profile
from pytrainer.athlete import Athlete
from pytrainer.test import DDBBTestCase


class AthleteTest(DDBBTestCase):

    def setUp(self):
        super().setUp()
        main = Mock()
        main.ddbb = self.ddbb
        main.profile = Profile()
        self.athlete = Athlete(parent=main)

    def tearDown(self):
        self.athlete = None
        super().tearDown()

    def test_athlete_insert_and_get(self):
        data = {'date': date(2017, 4, 3), 'weight': 60.0, 'bodyfat': 20.0,
                'restinghr': 60, 'maxhr': 190, 'id_athletestat': 1}
        self.athlete.insert_athlete_stats(str(data['date']), data['weight'],
                                          data['bodyfat'], data['restinghr'],
                                          data['maxhr'])
        data2 = tuple(self.athlete.get_athlete_stats())
        self.assertEqual(data, data2[0])

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
        data2 = tuple(self.athlete.get_athlete_stats())
        self.assertEqual(data, data2[0])

    def test_athlete_delete_record(self):
        data = {'date': date(2017, 4, 3), 'weight': 60.0, 'bodyfat': 20.0,
                'restinghr': 60, 'maxhr': 190, 'id_athletestat': 1}
        self.athlete.insert_athlete_stats(str(data['date']), data['weight'],
                                          data['bodyfat'], data['restinghr'],
                                          data['maxhr'])
        self.athlete.delete_record(1)
        self.assertFalse(tuple(self.athlete.get_athlete_stats()))
