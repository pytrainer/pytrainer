#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "David García Granda - dgranda@gmail.com"
__copyright__ = "Copyright (C) 2013 David García Granda"
__license__ = "GPLv2 or later"

import unittest
import os
import time
import mock
from pytrainer.record import Record
from pytrainer.lib.sqliteUtils import Sql

class RecordTest(unittest.TestCase):

    def setUp(self):
        self.mock_ddbb = mock.Mock(spec=Sql)
        self.test_record = Record(None)
        self.test_record.ddbb = self.mock_ddbb
        
    def tearDown(self):
        pass

    def test_getLastRecordDateString_nosport(self):
        try:
            self.test_record.ddbb.select.return_value = [(u'2013-03-18',)]
            last_entry_date = self.test_record.getLastRecordDateString()
            time.strptime(last_entry_date, "%Y-%m-%d")
            return True
        except():
            self.fail()

    def test_getLastRecordDateString_notfound(self):
        try:
            self.test_record.ddbb.select.return_value = [] # It also applies when no date is found for given sport_id
            last_entry_date = self.test_record.getLastRecordDateString()
            self.assertEquals(None, last_entry_date)
        except():
            self.fail()

if __name__ == '__main__':
    unittest.main()
