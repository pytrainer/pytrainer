#!/usr/bin/env python

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

from pytrainer.test.util.gettext_setup import gettext_setup
gettext_setup()

import unittest
import gpx
import os

class GpxTest(unittest.TestCase):
    def setUp(self):
        self.tmp_files = []
        
    def tearDown(self):
        for file_name in self.tmp_files:
            try:
                os.remove(file_name)
            except:
                pass
    
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
            g = gpx.Gpx(filename=file_name)
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
            g = gpx.Gpx(filename=file_name)
        except IndexError:
            self.fail("Gpx parser crashed on file with a nameless track")
        

if __name__ == '__main__':
    unittest.main()
