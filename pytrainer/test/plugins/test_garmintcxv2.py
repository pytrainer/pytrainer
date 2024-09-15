from unittest.mock import Mock
from lxml import etree

from pytrainer.plugins import Plugins
from pytrainer.core.activity import Activity
from pytrainer.test import DDBBTestCase


class GarminTCXv2PluginTest(DDBBTestCase):

    def setUp(self):
        super().setUp()
        main = Mock()
        main.ddbb = self.ddbb
        main.startup_options = Mock()
        main.profile = Mock()
        main.profile.plugindir = 'plugins'
        plugins = Plugins(parent=main)
        self.plugin = plugins.importClass('plugins/garmin-tcxv2')
        tree = etree.parse('pytrainer/test/imports/sample.tcx')
        self.activity = self.plugin.getActivities(tree)[0]

    def test_not_inDatabase(self):
        self.assertFalse(self.plugin.inDatabase(self.activity))

    def test_inDatabase(self):
        activity = Activity(date_time_utc='2012-10-14T10:02:42.000Z', sport_id='1')
        self.session.add(activity)
        self.session.commit()
        self.assertTrue(self.plugin.inDatabase(self.activity))

    def test_detailsFromTCX(self):
        self.assertEqual(self.plugin.detailsFromTCX(self.activity), '2012-10-14T10:02:42.000Z')
