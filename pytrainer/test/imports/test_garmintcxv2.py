#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "David García Granda – dgranda@gmail.com"
__copyright__ = "Copyright © 2013 David García Granda"
__license__ = "GPL v2 or later"

from unittest.mock import Mock
import os
import sys
from lxml import etree

from pytrainer.environment import Environment
from pytrainer.core.activity import Activity
from pytrainer.importdata import import_plugin_class
from pytrainer.test import DDBBTestCase


class GarminTCXv2Test(DDBBTestCase):

    def setUp(self):
        super().setUp()
        self.environment = Environment()
        self.parent = Mock()
        self.parent.parent = Mock()
        self.parent.parent.ddbb = self.ddbb
        sys.path.insert(0, os.path.join(self.environment.data_path, "imports"))

    def test_valid_file(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            tcx_file = current_path + "/sample.tcx"
            garmin_tcxv2 = import_plugin_class(self.environment, self.parent, "file_garmintcxv2.py")
            xmldoc = etree.parse(tcx_file)
            valid_xml = garmin_tcxv2.validate(xmldoc, "schemas/GarminTrainingCenterDatabase_v2.xsd")
            self.assertTrue(valid_xml)
        except():
            self.fail()

    def test_workout_summary(self):
        summary = [(0, False, '2012-10-14T12:02:42', '10.12', '00:39:51', 'Running')]
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            tcx_file = current_path + "/sample.tcx"
            garmin_tcxv2 = import_plugin_class(self.environment, self.parent, "file_garmintcxv2.py")
            garmin_tcxv2.xmldoc = etree.parse(tcx_file)
            garmin_tcxv2.buildActivitiesSummary()
            self.assertEqual(summary, garmin_tcxv2.activitiesSummary)
        except():
            self.fail()

    def test_summary_in_database(self):
        summary = [(0, True, '2012-10-14T12:02:42', '10.12', '00:39:51', 'Running')]
        activity = Activity(date_time_utc='2012-10-14T10:02:42Z', sport_id='1')
        self.session.add(activity)
        self.session.commit()
        current_path = os.path.dirname(os.path.abspath(__file__))
        tcx_file = current_path + "/sample.tcx"
        garmin_tcxv2 = import_plugin_class(self.environment, self.parent, "file_garmintcxv2.py")
        garmin_tcxv2.xmldoc = etree.parse(tcx_file)
        garmin_tcxv2.buildActivitiesSummary()
        self.assertEqual(summary, garmin_tcxv2.activitiesSummary)
