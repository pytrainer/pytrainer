# -*- coding: utf-8 -*-

#Copyright (C) David García Granda dgranda@users.sourceforge.net
#Copyright (C) Kevin Dwyer kevin@pheared.net

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

import unittest
import os
from tempfile import NamedTemporaryFile
from lxml import etree
from pytrainer.lib.gpx import Gpx

class GpxTest(unittest.TestCase):

    def setUp(self):
        self.tmp_files = []
        
    def tearDown(self):
        for file_name in self.tmp_files:
            try:
                os.remove(file_name)
            except:
                pass

    def test_get_laps_old(self):
        orig_laps = [
            ("1264.66","42.84154594","-2.68554166","426","5000.71875","42.83547375","-2.68631422","active","170","177","4.93775940","manual"),
            ("1279.71","42.86093295","-2.66849270","445","5162.37109","42.84155038","-2.68552473","active","176","179","5.10653210","manual"),
            ("1263.54","42.83505499","-2.67709371","423","4882.18457","42.86094376","-2.66848792","active","176","179","4.37805939","manual"),
            ("1525.68","42.84018606","-2.68670272","426","4973.64746","42.83504661","-2.67710888","active","167","181","4.52464294","manual"),
            ("374.23","42.83771038","-2.68647373","96","1098.94531","42.84018849","-2.68670733","active","159","163","4.30066299","manual")]
        try:
            xml_file = os.path.dirname(os.path.abspath(__file__)) + "/gpxplus_sample_old.gpx"
            gpx = Gpx(None, None) # avoid launching _getValues
            gpx.tree = etree.ElementTree(file = xml_file).getroot()
            gpx_laps = gpx.getLaps()
            self.assertEquals(orig_laps, gpx_laps)
        except():
            self.fail()

    def test_get_laps(self):
        orig_laps = [
            ("311.31","43.53781521","-5.63955233","81","1000.000000","43.54065232","-5.65094300","active","158","178","3.52099586","distance"),
            ("337.85","43.53220135","-5.63737772","83","1000.000000","43.53780859","-5.63955157","active","149","153","4.07694530","distance"),
            ("342.13","43.52516323","-5.64443462","87","1000.000000","43.53218752","-5.63737328","active","150","154","3.13006544","distance"),
            ("353.81","43.52035671","-5.65329663","86","1000.000000","43.52515301","-5.64443881","active","146","150","3.00786400","distance"),
            ("352.61","43.51314962","-5.65532908","87","1000.000000","43.52035412","-5.65329814","active","148","158","3.17764997","distance"),
            ("354.17","43.52061689","-5.65409191","87","1000.000000","43.51314115","-5.65533193","active","142","149","3.52461219","distance"),
            ("343.65","43.52592498","-5.64510651","86","1000.000000","43.52062519","-5.65408990","active","144","147","3.04636431","distance"),
            ("366.95","43.53079587","-5.63821390","83","1000.000000","43.52592733","-5.64509553","active","142","150","3.21967506","distance"),
            ("345.69","43.53726536","-5.63784711","87","1000.000000","43.53081406","-5.63820661","active","146","150","4.38874722","distance"),
            ("330.64","43.54042768","-5.64873822","86","1000.000000","43.53726494","-5.63783269","active","149","154","3.56236672","distance"),
            ("41.96","43.54054570","-5.65028653","11","132.227539","43.54043892","-5.64874199","active","150","152","3.40324497","manual")]
        try:
            xml_file = os.path.dirname(os.path.abspath(__file__)) + "/gpxplus_sample.gpx"
            gpx = Gpx(None, None) # avoid launching _getValues
            gpx.tree = etree.ElementTree(file = xml_file).getroot()
            gpx_laps = gpx.getLaps()
            self.assertEquals(orig_laps, gpx_laps)
        except():
            self.fail()

    def test_missing_tracks(self):
        trkdata = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" creator="" version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
</gpx>
"""
        
        # Write a GPX file with no tracks
        with NamedTemporaryFile(mode='w', delete=False) as tmpf:
            tmpf.write(trkdata)
        self.tmp_files.append(tmpf.name)
        
        try:
            g = Gpx(filename=tmpf.name)
        except IndexError:
            self.fail("Gpx parser crashed on file without tracks")

    def test_missing_name(self):
        trkdata = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" creator="" version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
<trk></trk>
</gpx>
"""
        
        # Write a GPX file with a nameless track
        with NamedTemporaryFile(mode='w', delete=False) as tmpf:
            tmpf.write(trkdata)
        self.tmp_files.append(tmpf.name)
        
        try:
            g = Gpx(filename=tmpf.name)
        except IndexError:
            self.fail("Gpx parser crashed on file with a nameless track")

if __name__ == '__main__':
    unittest.main()
