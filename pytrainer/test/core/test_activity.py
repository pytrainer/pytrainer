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

import datetime
from unittest.mock import Mock
from dateutil.tz import tzoffset
from sqlalchemy.orm.exc import NoResultFound

from pytrainer.lib.ddbb import DeclarativeBase
from pytrainer.profile import Profile
from pytrainer.lib.uc import UC
from pytrainer.core.activity import ActivityService, Laptrigger
from pytrainer.lib.date import DateRange
from pytrainer.test import DDBBTestCase


class ActivityTest(DDBBTestCase):

    def setUp(self):
        super().setUp()
        main = Mock()
        main.ddbb = self.ddbb
        main.profile = Profile()
        self.uc = UC()
        self.uc.set_us(False)
        self.service = ActivityService(pytrainer_main=main)
        records_table = DeclarativeBase.metadata.tables['records']
        self.ddbb.session.execute(records_table.insert(), {
            'distance': 46.18,
            'maxspeed': 44.6695617695,
            'maxpace': 1.2,
            'title': 'test activity',
            'unegative': 564.08076273,
            'upositive': 553.05993673,
            'average': 22.3882142185,
            'date_time_local': '2016-07-24 12:58:23+0300',
            'calories': 1462,
            'beats': 115.0,
            'comments': 'test comment',
            'pace': 2.4,
            'date_time_utc': '2016-07-24T09:58:23Z',
            'date': datetime.date(2016, 7, 24),
            'duration': 7426,
            'sport': 1,
            'maxbeats': 120.0})
        laps_table = DeclarativeBase.metadata.tables['laps']
        self.ddbb.session.execute(laps_table.insert(), {
            'distance': 46181.9,
            'lap_number': 0,
            'calories': 1462,
            'elapsed_time': '7426.0',
            'record': 1,
            'intensity': 'active',
            'avg_hr': 136,
            'max_hr': 173,
            'laptrigger': 'manual'})
        self.activity = self.service.get_activity(1)

    def tearDown(self):
        self.service.clear_pool()
        self.uc.set_us(False)
        super().tearDown()

    def test_activity_date_time(self):
        self.assertEqual(self.activity.date_time, datetime.datetime(2016, 7, 24,
                                                                        12, 58, 23,
                                                    tzinfo=tzoffset(None, 10800)))

    def test_activity_distance(self):
        self.assertEqual(self.activity.distance, 46.18)

    def test_activity_sport_name(self):
        self.assertEqual(self.activity.sport_name, 'Mountain Bike')

    def test_activity_duration(self):
        self.assertEqual(self.activity.duration, 7426)

    def test_activity_time(self):
        self.assertEqual(self.activity.time, self.activity.duration)

    def test_activity_starttime(self):
        self.assertEqual(self.activity.starttime, '12:58:23')

    def test_activity_time_tuple(self):
        self.assertEqual(self.activity.time_tuple, (2, 3, 46))

    def test_activity_lap(self):
        self.maxDiff = None
        self.assertEqual(
            self.activity.laps[0],
            {
                'distance': 46181.9,
                'end_lon': None,
                'lap_number': 0,
                'start_lon': None,
                'id_lap': 1,
                'calories': 1462,
                'comments': None,
                'laptrigger': Laptrigger.MANUAL,
                'elapsed_time': '7426.0',
                'record': 1,
                'intensity': 'active',
                'avg_hr': 136,
                'max_hr': 173,
                'end_lat': None,
                'start_lat': None,
                'max_speed': None},
        )
        lap = self.activity.Laps[0]
        self.assertEqual(lap.distance, 46181.9)
        self.assertEqual(lap.duration, 7426.0)
        self.assertEqual(lap.calories, 1462)
        self.assertEqual(lap.avg_hr, 136)
        self.assertEqual(lap.max_hr, 173)
        self.assertEqual(lap.activity, self.activity)
        self.assertEqual(lap.lap_number, 0)
        self.assertEqual(lap.intensity, u'active')
        self.assertEqual(lap.laptrigger, Laptrigger.MANUAL)

    def test_activity_get_value_f(self):
        self.assertEqual(self.activity.get_value_f('distance', "%0.2f"), '46.18')
        self.assertEqual(self.activity.get_value_f('average', "%0.2f"), '22.39')
        self.assertEqual(self.activity.get_value_f('maxspeed', "%0.2f"), '44.67')
        self.assertEqual(self.activity.get_value_f('time', '%s'), '2:03:46')
        self.assertEqual(self.activity.get_value_f('calories', "%0.0f"), '1462')
        self.assertEqual(self.activity.get_value_f('pace', "%s"), '2:40')
        self.assertEqual(self.activity.get_value_f('maxpace', "%s"), '1:20')
        self.assertEqual(self.activity.get_value_f('upositive', "%0.2f"), '553.06')
        self.assertEqual(self.activity.get_value_f('unegative', "%0.2f"), '564.08')

    def test_activity_get_value_f_us(self):
        self.uc.set_us(True)
        self.assertEqual(self.activity.get_value_f('distance', "%0.2f"), '28.69')
        self.assertEqual(self.activity.get_value_f('average', "%0.2f"), '13.91')
        self.assertEqual(self.activity.get_value_f('maxspeed', "%0.2f"), '27.76')
        self.assertEqual(self.activity.get_value_f('time', '%s'), '2:03:46')
        self.assertEqual(self.activity.get_value_f('calories', "%0.0f"), '1462')
        self.assertEqual(self.activity.get_value_f('pace', "%s"), '4:17')
        self.assertEqual(self.activity.get_value_f('maxpace', "%s"), '2:09')
        self.assertEqual(self.activity.get_value_f('upositive', "%0.2f"), '1814.50')
        self.assertEqual(self.activity.get_value_f('unegative', "%0.2f"), '1850.66')

    def test_activity_service_null(self):
        none_activity = self.service.get_activity(None)
        self.assertIsNone(none_activity.id)

    def test_activity_remove(self):
        self.service.remove_activity_from_db(self.activity)
        try:
            self.service.get_activity(1)
        except NoResultFound:
            pass
        else:
            self.fail()

    def test_activities_for_day(self):
        activity = list(self.service.get_activities_for_day(datetime.date(2016, 7, 24)))[0]
        self.assertEqual(self.activity, activity)

    def test_activities_period(self):
        activity = list(self.service.get_activities_period(DateRange.for_week_containing(datetime.date(2016, 7, 24))))[0]
        self.assertEqual(self.activity, activity)

    def test_all_activities(self):
        activity = list(self.service.get_all_activities())[0]
        self.assertEqual(self.activity, activity)
