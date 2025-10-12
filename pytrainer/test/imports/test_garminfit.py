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
from pytrainer.importdata import import_plugin_class
from pytrainer.test import DDBBTestCase


class GarminFitTest(DDBBTestCase):

    def setUp(self):
        super().setUp()
        self.environment = Environment()
        self.parent = Mock()
        self.parent.parent = Mock()
        self.parent.parent.ddbb = self.ddbb

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
