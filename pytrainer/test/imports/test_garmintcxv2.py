#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "David García Granda – dgranda@gmail.com"
__copyright__ = "Copyright © 2013 David García Granda"
__license__ = "GPL v2 or later"

import unittest
import os
import mock
from lxml import etree
from imports.file_garmintcxv2 import garmintcxv2
from pytrainer.lib.ddbb import DDBB
from pytrainer.core.activity import Activity

class GarminTCXv2Test(unittest.TestCase):

    def setUp(self):
        self.ddbb = DDBB()
        self.ddbb.connect()
        self.ddbb.create_tables(add_default=True)
        self.parent = mock.Mock()
        self.parent.parent = mock.Mock()
        self.parent.parent.ddbb = self.ddbb

    def tearDown(self):
        self.ddbb.disconnect()
        self.ddbb.drop_tables()

    def test_valid_file(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path))) + "/"
            tcx_file = current_path + "/sample.tcx"
            garmin_tcxv2 = garmintcxv2(None, data_path)
            xmldoc = etree.parse(tcx_file)
            valid_xml = garmin_tcxv2.validate(xmldoc, "schemas/GarminTrainingCenterDatabase_v2.xsd")
            self.assertTrue(valid_xml)
        except():
            self.fail()

    def test_workout_summary(self):
        summary = [(0, False, '2012-10-14T12:02:42', '10.12', '00:39:51', 'Running')]
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path))) + "/"
            tcx_file = current_path + "/sample.tcx"
            garmin_tcxv2 = garmintcxv2(self.parent, data_path)
            garmin_tcxv2.xmldoc = etree.parse(tcx_file)
            garmin_tcxv2.buildActivitiesSummary()
            self.assertEqual(summary, garmin_tcxv2.activitiesSummary)
        except():
            self.fail()

    def test_summary_in_database(self):
        summary = [(0, True, '2012-10-14T12:02:42', '10.12', '00:39:51', 'Running')]
        activity = Activity(date_time_utc='2012-10-14T10:02:42Z', sport_id='1')
        self.ddbb.session.add(activity)
        self.ddbb.session.commit()
        current_path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path))) + "/"
        tcx_file = current_path + "/sample.tcx"
        garmin_tcxv2 = garmintcxv2(self.parent, data_path)
        garmin_tcxv2.xmldoc = etree.parse(tcx_file)
        garmin_tcxv2.buildActivitiesSummary()
        self.assertEqual(summary, garmin_tcxv2.activitiesSummary)

if __name__ == '__main__':
    unittest.main()
