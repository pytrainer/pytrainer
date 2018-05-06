import os
import datetime
import mock

from gi.repository import Gtk
from unittest import TestCase
from pytrainer.lib.ddbb import DDBB
from pytrainer.lib.localization import initialize_gettext
from pytrainer.core.sport import SportService
from pytrainer.environment import Environment
from pytrainer.profile import Profile
from pytrainer.record import Record
from pytrainer.core.activity import Activity
initialize_gettext('locale/')

from pytrainer.gui.windowmain import Main
from pytrainer.lib.listview import ListSearch
from pytrainer.lib.uc import UC

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

class ListviewTest(TestCase):

    def setUp(self):
        env = Environment()
        env.data_path = os.curdir
        env.create_directories()
        self.main = mock.Mock()
        self.main.ddbb = DDBB()
        self.main.ddbb.connect()
        self.main.ddbb.create_tables()
        self.main.profile = Profile()
        self.main.uc = UC()
        self.sport_service = SportService(self.main.ddbb)
        self.main.record = Record(self.sport_service, parent=self.main)
        self.parent = Main(self.sport_service, parent=self.main)
        self.main.ddbb.session.add(Activity(sport=self.sport_service.get_sport(1),
                                            date=datetime.datetime(2018, 5, 6, 10, 0, 0),
                                            duration=1000, distance=25))
        self.main.ddbb.session.add(Activity(sport=self.sport_service.get_sport(2),
                                            date=datetime.datetime(2018, 1, 6, 10, 0, 0),
                                            duration=10000, distance=100))
        self.main.ddbb.session.commit()

    def tearDown(self):
        self.main.ddbb.disconnect()
        self.main.ddbb.drop_tables()

    def test_listsearch_all(self):
        self.assertEqual(len(list(self.main.record.getRecordListByCondition(None))), 2)

    def test_listsearch_defaults(self):
        self.assertEqual(len(list(self.main.record.getRecordListByCondition(self.parent.listsearch.condition))), 2)

    def test_listsearch_sport(self):
        self.parent.lsa_sport.set_active(1)
        self.assertEqual(len(list(self.main.record.getRecordListByCondition(self.parent.listsearch.condition))), 1)

    def test_listsearch_distance(self):
        self.parent.lsa_distance.set_active(4)
        self.assertEqual(len(list(self.main.record.getRecordListByCondition(self.parent.listsearch.condition))), 1)

    def test_listsearch_duration(self):
        self.parent.lsa_duration.set_active(1)
        self.assertEqual(len(list(self.main.record.getRecordListByCondition(self.parent.listsearch.condition))), 1)
