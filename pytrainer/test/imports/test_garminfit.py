#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "David García Granda – dgranda@gmail.com"
__copyright__ = "Copyright © 2013 David García Granda"
__license__ = "GPL v2 or later"

import unittest
from unittest.mock import Mock
import os
import sys
from lxml import etree

from pytrainer.environment import Environment
from pytrainer.lib.ddbb import DDBB
from pytrainer.importdata import import_plugin_class


class GarminFitTest(unittest.TestCase):

    def setUp(self):
        self.ddbb = DDBB()
        self.ddbb.connect()
        self.ddbb.create_tables(add_default=True)
        self.environment = Environment()
        self.parent = Mock()
        self.parent.parent = Mock()
        self.parent.parent.ddbb = self.ddbb

    def tearDown(self):
        self.ddbb.disconnect()
        self.ddbb.drop_tables()

    def test_parse_fit_file(self):
        try:
            current_path = os.path.dirname(os.path.abspath(__file__))
            fit_file = current_path + "/sample.fit"
            sys.path.insert(0, os.path.join(self.environment.data_path, "imports"))
            garmin_fit = import_plugin_class(self.environment, self.parent, "file_garminfit.py")
            xmldoc = etree.fromstring(garmin_fit.fromFIT2TCXv2(fit_file))
            valid_xml = garmin_fit.validate(xmldoc, "schemas/GarminTrainingCenterDatabase_v2.xsd")
            self.assertTrue(valid_xml)
        except():
            self.fail()

if __name__ == '__main__':
    unittest.main()
