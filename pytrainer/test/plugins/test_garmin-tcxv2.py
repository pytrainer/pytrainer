import unittest
import os
import mock
from lxml import etree

from pytrainer.plugins import Plugins
from pytrainer.lib.ddbb import DDBB
from pytrainer.core.activity import Activity

class GarminTCXv2PluginTest(unittest.TestCase):

    def setUp(self):
        self.ddbb = DDBB()
        self.ddbb.connect()
        self.ddbb.create_tables(add_default=True)
        main = mock.Mock()
        main.ddbb = self.ddbb
        main.startup_options = mock.Mock()
        main.profile = mock.Mock()
        main.profile.plugindir = 'plugins'
        plugins = Plugins(parent=main)
        self.plugin = plugins.importClass('plugins/garmin-tcxv2')
        tree = etree.parse('pytrainer/test/imports/sample.tcx')
        self.activity = self.plugin.getActivities(tree)[0]

    def tearDown(self):
        self.ddbb.disconnect()
        self.ddbb.drop_tables()

    def test_not_inDatabase(self):
        self.assertFalse(self.plugin.inDatabase(self.activity))

    def test_inDatabase(self):
        activity = Activity(date_time_utc='2012-10-14T10:02:42.000Z', sport_id='1')
        self.ddbb.session.add(activity)
        self.ddbb.session.commit()
        self.assertTrue(self.plugin.inDatabase(self.activity))

    def test_detailsFromTCX(self):
        self.assertEquals(self.plugin.detailsFromTCX(self.activity), '2012-10-14T10:02:42.000Z')
