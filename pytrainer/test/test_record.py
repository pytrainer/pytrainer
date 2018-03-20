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
import mock
from datetime import datetime
from dateutil.tz import tzoffset
from pytrainer.lib.ddbb import DDBB
from pytrainer.core.sport import SportService
from pytrainer.record import Record
from pytrainer.core.activity import ActivityService

class RecordTest(unittest.TestCase):

    def setUp(self):
        self.ddbb = DDBB()
        self.ddbb.connect()
        self.ddbb.create_tables(add_default=True)
        self.main = mock.Mock()
        self.main.ddbb = self.ddbb
        self.main.activitypool = ActivityService(pytrainer_main=self.main)
        self.main.profile.gpxdir = '/nonexistent'
        self.record = Record(SportService(self.ddbb), parent=self.main)
        time = 7426
        distance = 46.18
        speed = distance * 3600 / time
        time_hhmmss = [time // 3600, (time / 60) % 60, time % 60]
        self.summary = {}
        self.summary['rcd_gpxfile'] = u'/nonexistent'
        self.summary['rcd_sport'] = u"Run"
        self.summary['rcd_date'] = u'2016-07-24'
        self.summary['rcd_calories'] = 1462
        self.summary['rcd_comments'] = u'test comment'
        self.summary['rcd_title'] = u'test 1'
        self.summary['rcd_time'] = time_hhmmss
        self.summary['rcd_distance'] = "%0.2f" %distance
        self.summary['rcd_pace'] = "%d.%02d" % ((3600 / speed) / 60, (3600 / speed) % 60)
        self.summary['rcd_maxpace'] = "%d.%02d" %((3600 / 72) / 60, (3600 / 72)% 60)
        self.summary['rcd_average'] = speed
        self.summary['rcd_maxvel'] = 72
        self.summary['rcd_beats'] = 115.0
        self.summary['rcd_maxbeats'] = 120
        self.summary['rcd_upositive'] = 553.1
        self.summary['rcd_unegative'] = 564.1
        self.summary['date_time_local'] = u'2016-07-24 12:58:23+03:00'
        self.summary['date_time_utc'] = u'2016-07-24T09:58:23Z'
        self.laps = [{'distance': 46181.9,
                      'lap_number': 0,
                      'calories': 1462,
                      'elapsed_time': u'7426.0',
                      'intensity': u'active',
                      'avg_hr': 136,
                      'max_hr': 173,
                      'laptrigger': u'manual'}]

    def tearDown(self):
        self.ddbb.disconnect()
        self.ddbb.drop_tables()

    def test_insert_record(self):
        newid = self.record.insertRecord(self.summary, laps=self.laps)
        activity = self.main.activitypool.get_activity(newid)
        self.assertEquals(activity.unegative, 564.1)
        self.assertEquals(activity.upositive, 553.1)
        self.assertEquals(activity.beats, 115.0)
        self.assertEquals(activity.maxbeats, 120)
        self.assertEquals(activity.date_time, datetime(2016, 7, 24, 12, 58, 23,
                                                       tzinfo=tzoffset(None, 10800)))
        self.assertEquals(activity.date_time_utc, u'2016-07-24T09:58:23Z')
        self.assertEquals(activity.sport, self.record._sport_service.get_sport_by_name(u"Run"))
        self.assertEquals(activity.title, u'test 1')
        self.assertEquals(activity.laps[0], {'distance': 46181.9, 'end_lon': None, 'lap_number': 0, 'start_lon': None, 'id_lap': 1, 'calories': 1462, 'comments': None, 'laptrigger': u'manual', 'elapsed_time': u'7426.0', 'record': 1, 'intensity': u'active', 'avg_hr': 136, 'max_hr': 173, 'end_lat': None, 'start_lat': None, 'max_speed': None})

    def test_insert_record_datetime(self):
        """Importing multiple activities uses a datetime object for
list_options['date_time_local'], also test that code path"""
        self.summary['date_time_local'] = datetime(2016, 7, 24, 12, 58, 23, tzinfo=tzoffset(None, 10800))
        newid = self.record.insertRecord(self.summary, laps=self.laps)
        activity = self.main.activitypool.get_activity(newid)
        self.assertEquals(activity.unegative, 564.1)
        self.assertEquals(activity.upositive, 553.1)
        self.assertEquals(activity.beats, 115.0)
        self.assertEquals(activity.maxbeats, 120)
        self.assertEquals(activity.date_time, datetime(2016, 7, 24, 12, 58, 23,
                                                       tzinfo=tzoffset(None, 10800)))
        self.assertEquals(activity.date_time_utc, u'2016-07-24T09:58:23Z')
        self.assertEquals(activity.sport, self.record._sport_service.get_sport_by_name(u"Run"))
        self.assertEquals(activity.title, u'test 1')
        self.assertEquals(activity.laps[0], {'distance': 46181.9, 'end_lon': None, 'lap_number': 0, 'start_lon': None, 'id_lap': 1, 'calories': 1462, 'comments': None, 'laptrigger': u'manual', 'elapsed_time': u'7426.0', 'record': 1, 'intensity': u'active', 'avg_hr': 136, 'max_hr': 173, 'end_lat': None, 'start_lat': None, 'max_speed': None})

    def test_update_record(self):
        newid = self.record.insertRecord(self.summary)
        update_dict = self.summary.copy()
        update_dict['rcd_title'] = u'test 2'
        update_dict['rcd_sport'] = u"Bike"
        self.record.updateRecord(update_dict, newid)
        activity = self.main.activitypool.get_activity(newid)
        self.assertEquals(activity.title, u'test 2')
        self.assertEquals(activity.sport, self.record._sport_service.get_sport_by_name(u"Bike"))

    def test_get_day_list(self):
        self.record.insertRecord(self.summary)
        daylist = list(self.record.getRecordDayList(datetime(2016, 7, 24, 9, 58, 23)))
        self.assertEquals(daylist, [24])
