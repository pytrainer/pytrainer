#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "David García Granda - dgranda@gmail.com"
__copyright__ = "Copyright (C) 2013 David García Granda"
__license__ = "GPL v2 or later"

import unittest
import os
from lxml import etree
from imports.file_garmintcxv2 import garmintcxv2

class GarminTCXv2Test(unittest.TestCase):
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
        summary = [(0, False, '2012-10-14T10:02:42', '10.12', '00:39:51', 'Running')]
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path))) + "/"
            tcx_file = current_path + "/sample.tcx"
            garmin_tcxv2 = garmintcxv2(None, data_path)
            garmin_tcxv2.xmldoc = etree.parse(tcx_file)
            garmin_tcxv2.buildActivitiesSummary()
            self.assertEquals(summary, garmin_tcxv2.activitiesSummary)
        except():
            self.fail()

if __name__ == '__main__':
    unittest.main()
