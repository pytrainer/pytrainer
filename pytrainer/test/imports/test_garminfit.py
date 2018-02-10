#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "David García Granda - dgranda@gmail.com"
__copyright__ = "Copyright (C) 2013 David García Granda"
__license__ = "GPL v2 or later"

import unittest
import os
import mock
from lxml import etree
from imports.file_garminfit import garminfit
from pytrainer.lib.ddbb import DDBB

class GarminFitTest(unittest.TestCase):

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

    def test_parse_fit_file(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path))) + "/"
            fit_file = current_path + "/sample.fit"
            garmin_fit = garminfit(self.parent, data_path)
            xmldoc = etree.fromstring(garmin_fit.fromFIT2TCXv2(fit_file))
            valid_xml = garmin_fit.validate(xmldoc, "schemas/GarminTrainingCenterDatabase_v2.xsd")
            self.assertTrue(valid_xml)
        except():
            self.fail()

if __name__ == '__main__':
    unittest.main()
