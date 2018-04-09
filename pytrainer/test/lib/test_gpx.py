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
from lxml import etree
from pytrainer.lib.gpx import Gpx

class GpxTest(unittest.TestCase):

    def setUp(self):
        self.tmp_files = []
        self.xml_files = [os.path.dirname(os.path.abspath(__file__)) + fname for fname in ("/gpxplus_sample_cluehr.gpx", "/gpxplus_sample_garminhr.gpx")]
        self.reference_track = [(0, 497.4, 4.0, 0, 37.3012, 12.3456789, 76, None, None),
                                (0.0885381292497543, 497.5, 4.0, 106.24575509970515, 37.301205, 12.3466789, 78, None, None),
                                (0.1770762584995086, 498.0, 4.0, 212.4915101994103, 37.3012, 12.3476789, 80, None, None),
                                (0.2656183143087815, 499.0, 4.0, 318.74197717053784, 37.301209, 12.3486789, 79, None, None),
                                (0.35416037011805446, 500.0, 4.0, 318.7466890419602, 37.3012, 12.3496789, 83, None, None)]
        self.ref_laps = [(0.35416037011805446, 497.4, 4, 212.50093394225507, 37.3012, 12.3456789, 76, None, None),
                         (0.44269849936780875, 497.5, 4, 212.4962220708327, 37.301205, 12.3466789, 78, None, None),
                         (0.531236628617563, 498.0, 4, 212.4915101994103, 37.3012, 12.3476789, 80, None, None),
                         (0.619778684426836, 499.0, 4, 318.74197717053784, 37.301209, 12.3486789, 79, None, None),
                         (0.708320740236109, 500.0, 4, 318.7466890419602, 37.3012, 12.3496789, 83, None, None)]

        
    def tearDown(self):
        for file_name in self.tmp_files:
            try:
                os.remove(file_name)
            except:
                pass

    def test_get_laps_old(self):
        orig_laps = [
            (1264.66,42.84154594,-2.68554166,426,5000.71875,42.83547375,-2.68631422,"active",170,177,4.93775940,"manual"),
            (1279.71,42.86093295,-2.66849270,445,5162.37109,42.84155038,-2.68552473,"active",176,179,5.10653210,"manual"),
            (1263.54,42.83505499,-2.67709371,423,4882.18457,42.86094376,-2.66848792,"active",176,179,4.37805939,"manual"),
            (1525.68,42.84018606,-2.68670272,426,4973.64746,42.83504661,-2.67710888,"active",167,181,4.52464294,"manual"),
            ( 374.23,42.83771038,-2.68647373, 96,1098.94531,42.84018849,-2.68670733,"active",159,163,4.30066299,"manual")]
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
            (311.31,43.53781521,-5.63955233,81,1000.000000,43.54065232,-5.65094300,"active",158,178,3.52099586,"distance"),
            (337.85,43.53220135,-5.63737772,83,1000.000000,43.53780859,-5.63955157,"active",149,153,4.07694530,"distance"),
            (342.13,43.52516323,-5.64443462,87,1000.000000,43.53218752,-5.63737328,"active",150,154,3.13006544,"distance"),
            (353.81,43.52035671,-5.65329663,86,1000.000000,43.52515301,-5.64443881,"active",146,150,3.00786400,"distance"),
            (352.61,43.51314962,-5.65532908,87,1000.000000,43.52035412,-5.65329814,"active",148,158,3.17764997,"distance"),
            (354.17,43.52061689,-5.65409191,87,1000.000000,43.51314115,-5.65533193,"active",142,149,3.52461219,"distance"),
            (343.65,43.52592498,-5.64510651,86,1000.000000,43.52062519,-5.65408990,"active",144,147,3.04636431,"distance"),
            (366.95,43.53079587,-5.63821390,83,1000.000000,43.52592733,-5.64509553,"active",142,150,3.21967506,"distance"),
            (345.69,43.53726536,-5.63784711,87,1000.000000,43.53081406,-5.63820661,"active",146,150,4.38874722,"distance"),
            (330.64,43.54042768,-5.64873822,86,1000.000000,43.53726494,-5.63783269,"active",149,154,3.56236672,"distance"),
            ( 41.96,43.54054570,-5.65028653,11, 132.227539,43.54043892,-5.64874199,"active",150,152,3.40324497,"manual")]
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
        file_name = "test-missing.gpx"
        tmpf = file(file_name,'w')
        tmpf.write(trkdata)
        tmpf.close()
        self.tmp_files.append(file_name)
        
        try:
            g = Gpx(filename=file_name)
        except IndexError:
            self.fail("Gpx parser crashed on file without tracks")

    def test_missing_name(self):
        trkdata = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" creator="" version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
<trk></trk>
</gpx>
"""
        
        # Write a GPX file with a nameless track
        file_name = "test-noname.gpx"
        tmpf = file(file_name,'w')
        tmpf.write(trkdata)
        tmpf.close()
        self.tmp_files.append(file_name)
        
        try:
            g = Gpx(filename=file_name)
        except IndexError:
            self.fail("Gpx parser crashed on file with a nameless track")

    def test_getMaxValues(self):
        try:
            for xml_file_path in self.xml_files:
                gpx = Gpx(None, xml_file_path)
                total_dist, total_time, maxvel, maxhr = gpx.getMaxValues()
                self.assertEquals(0.35416037011805446, total_dist)
                self.assertEquals(4.0                , total_time)
                self.assertEquals(318.7466890419602  , maxvel)
                self.assertEquals(83                 , maxhr)
        except():
            self.fail()

    def test_getDate(self):
        try:
            for xml_file_path in self.xml_files:
                gpx = Gpx(None, xml_file_path)
                date = gpx.getDate()
                self.assertEquals('2018-03-25', date)
        except():
            self.fail()

    def test_getTrackRoutes(self):
        try:
            for xml_file_path in self.xml_files:
                gpx = Gpx(None, xml_file_path)
                tracks = gpx.getTrackRoutes()
                self.assertEquals([('Evening Ride', '2018-03-25')], tracks)
        except():
            self.fail()

    def test_getUnevenness(self):
        try:
            for xml_file_path in self.xml_files:
                gpx = Gpx(None, xml_file_path)
                upositive, unegative = gpx.getUnevenness()
                self.assertEquals(2.6000000000000227, upositive)
                self.assertEquals(0.0               , unegative)
        except():
            self.fail()

    def test_getTrackList(self):
        try:
            for xml_file_path in self.xml_files:
                gpx = Gpx(None, xml_file_path)
                values = gpx.getTrackList()
                if values[0][2] == 0.0:
                    # workaround: in some cases the total_time is not provided
                    track_mod = [e[:2]+(0.0,)+e[3:] for e in self.reference_track]
                    self.assertEquals(track_mod, values)
                else:
                    self.assertEquals(self.reference_track, values)
        except():
            self.fail()

    def test_getHeartRateAverage(self):
        try:
            for xml_file_path in self.xml_files:
                gpx = Gpx(None, xml_file_path)
                avg_hr = gpx.getHeartRateAverage()
                self.assertEquals(79, avg_hr)
        except():
            self.fail()

    def test_getCalories(self):
        try:
            for xml_file_path in self.xml_files:
                gpx = Gpx(None, xml_file_path)
                calories = gpx.getCalories()
                self.assertEquals(0, calories)
        except():
            self.fail()

    def test_getStart_time(self):
        try:
            for xml_file_path in self.xml_files:
                gpx = Gpx(None, xml_file_path)
                start_time = gpx.getStart_time()
                self.assertEquals('19:13:17', start_time)
        except():
            self.fail()

    def test_getLaps(self):
        try:
            for xml_file_path in self.xml_files:
                gpx = Gpx(None, xml_file_path)
                laps = gpx.getLaps()
                self.assertEquals([(4.0, 37.3012, 12.3496789, 0, 354.16037011805446, 37.3012, 12.3456789, 'active', 79, 83, 318.7466890419602, 'manual')], laps)
        except():
            self.fail()

    def test_getValues(self):
        try:
            for xml_file_path in self.xml_files:
                gpx = Gpx(None, xml_file_path)
                laps = gpx._getValues()
                if laps[0][2] == 0:
                    # workaround: in some cases the total_time is not provided
                    ref_mod = [e[:2]+(0.0,)+e[3:] for e in self.ref_laps]
                    self.assertEquals(ref_mod, laps)
                else:
                    self.assertEquals(self.ref_laps, laps)
        except():
            self.fail()

    def test_distance_between_points(self):
        test_data = [( 53.508289843586624, 127.32382305062322, 55.5701327091,  -3.98783805857,  7103.71421364501       ),
                     ( 27.60056779       , -96.5512591626    , 29.345904648 , 107.65956974   , 13191.597025234689      ),
                     (  8.994154802      ,  10.062921749     , 12.844728787 ,   6.52630260917,   577.0619145903964     ),
                     ( 48.0              ,  13.0             , 48.0001      ,  13.0          ,     0.01112989616565206 ),
                     ( 48.0              ,  13.0             , 48.0         ,  13.0001       ,     0.007447330361866163)]
        try:
            for lat1, lon1, lat2, lon2, dist in test_data:
                calc_dist = Gpx._distance_between_points(lat1, lon1, lat2, lon2)
                self.assertEquals(calc_dist, dist)
        except():
            self.fail()

    def test_calculate_speed(self):
        try:
            for xml_file_path in self.xml_files:
                gpx = Gpx(None, xml_file_path)
                velocity = gpx._calculate_speed(1337.0, 10.0)
                self.assertEquals(160652.50093394224, velocity)
        except():
            self.fail()

    def test_getStartTimeFromGPX(self):
        try:
            for xml_file_path in self.xml_files:
                gpx = Gpx(None, xml_file_path)
                utc_date_time, local_date_time = gpx.getStartTimeFromGPX("")
                self.assertEquals("2018-03-25T17:13:17Z", utc_date_time)
                self.assertEquals("2018-03-25 19:13:17+02:00", str(local_date_time))
        except():
            self.fail()

if __name__ == '__main__':
    unittest.main()
