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
import datetime
from mock import Mock
from dateutil.tz import tzoffset
from sqlalchemy.orm.exc import NoResultFound

from pytrainer.lib.ddbb import DDBB, DeclarativeBase
from pytrainer.profile import Profile
from pytrainer.lib.uc import UC
from pytrainer.core.activity import ActivityService

class ActivityTest(unittest.TestCase):

    def setUp(self):
        profile = Mock()
        profile.getValue = Mock(return_value='memory')
        self.ddbb = DDBB(profile)
        main = Mock()
        main.ddbb = self.ddbb
        main.profile = Profile()
        main.ddbb.connect()
        main.ddbb.create_tables(add_default=True) # We need a sport
        self.uc = UC()
        self.uc.set_us(False)
        self.service = ActivityService(pytrainer_main=main)
        records_table = DeclarativeBase.metadata.tables['records']
        self.ddbb.session.execute(records_table.insert({'distance': 46.18,
                                                            'maxspeed': 44.6695617695,
                                                            'maxpace': 1.2,
                                                            'title': u'test activity',
                                                            'unegative': 564.08076273,
                                                            'upositive': 553.05993673,
                                                            'average': 22.3882142185,
                                                            'date_time_local': u'2016-07-24 12:58:23+0300',
                                                            'calories': 1462,
                                                            'beats': 115.0,
                                                            'comments': u'test comment',
                                                            'pace': 2.4,
                                                            'date_time_utc': u'2016-07-24T09:58:23Z',
                                                            'date': datetime.date(2016, 7, 24),
                                                            'duration': 7426,
                                                            'sport': 1,
                                                            'maxbeats': 120.0}))
        laps_table = DeclarativeBase.metadata.tables['laps']
        self.ddbb.session.execute(laps_table.insert({'distance': 46181.9107741,
                                                     'lap_number': 0,
                                                     'calories': 1462,
                                                         'elapsed_time': u'7426.0',
                                                         'record': 1,
                                                         'intensity': u'active',
                                                         'avg_hr': 136,
                                                         'max_hr': 173,
                                                         'laptrigger': u'manual'}))
        self.activity = self.service.get_activity(1)

    def tearDown(self):
        self.service = None
        self.ddbb.disconnect()
        self.ddbb = None
        self.uc.set_us(False)

    def test_activity_date_time(self):
        self.assertEquals(self.activity.date_time, datetime.datetime(2016, 7, 24,
                                                                        12, 58, 23,
                                                    tzinfo=tzoffset(None, 10800)))

    def test_activity_distance(self):
        self.assertEquals(self.activity.distance, 46.18)

    def test_activity_sport_name(self):
        self.assertEquals(self.activity.sport_name, 'Mountain Bike')

    def test_activity_duration(self):
        self.assertEquals(self.activity.duration, 7426)

    def test_activity_time(self):
        self.assertEquals(self.activity.time, self.activity.duration)

    def test_activity_starttime(self):
        self.assertEquals(self.activity.starttime, '12:58:23 PM')

    def test_activity_time_tuple(self):
        self.assertEquals(self.activity.time_tuple, (2, 3, 46))

    def test_activity_lap(self):
        self.assertEquals(self.activity.laps[0], {'distance': 46181.9107741, 'end_lon': None, 'lap_number': 0, 'start_lon': None, 'id_lap': 1, 'calories': 1462, 'comments': None, 'laptrigger': u'manual', 'elapsed_time': u'7426.0', 'record': 1, 'intensity': u'active', 'avg_hr': 136, 'max_hr': 173, 'end_lat': None, 'start_lat': None, 'max_speed': None})

    def test_activity_get_value_f(self):
        self.assertEquals(self.activity.get_value_f('distance', "%0.2f"), '46.18')
        self.assertEquals(self.activity.get_value_f('average', "%0.2f"), '22.39')
        self.assertEquals(self.activity.get_value_f('maxspeed', "%0.2f"), '44.67')
        self.assertEquals(self.activity.get_value_f('time', '%s'), '2:03:46')
        self.assertEquals(self.activity.get_value_f('calories', "%0.0f"), '1462')
        self.assertEquals(self.activity.get_value_f('pace', "%s"), '2:24')
        self.assertEquals(self.activity.get_value_f('maxpace', "%s"), '1:12')
        self.assertEquals(self.activity.get_value_f('upositive', "%0.2f"), '553.06')
        self.assertEquals(self.activity.get_value_f('unegative', "%0.2f"), '564.08')

    def test_activity_get_value_f_us(self):
        self.uc.set_us(True)
        self.assertEquals(self.activity.get_value_f('distance', "%0.2f"), '28.69')
        self.assertEquals(self.activity.get_value_f('average', "%0.2f"), '13.91')
        self.assertEquals(self.activity.get_value_f('maxspeed', "%0.2f"), '27.76')
        self.assertEquals(self.activity.get_value_f('time', '%s'), '2:03:46')
        self.assertEquals(self.activity.get_value_f('calories', "%0.0f"), '1462')
        self.assertEquals(self.activity.get_value_f('pace', "%s"), '3:52')
        self.assertEquals(self.activity.get_value_f('maxpace', "%s"), '1:56')
        self.assertEquals(self.activity.get_value_f('upositive', "%0.2f"), '1814.50')
        self.assertEquals(self.activity.get_value_f('unegative', "%0.2f"), '1850.66')

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
