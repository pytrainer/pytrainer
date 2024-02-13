# -*- coding: utf-8 -*-

#Copyright (C)

#Based on plugin by Fiz Vazquez vud1@sindominio.net

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

import os
import logging
from lxml import etree

from pytrainer.lib.xmlUtils import XMLParser
from pytrainer.gui.dialogs import fileChooserDialog, guiFlush
from pytrainer.core.activity import Activity
from sqlalchemy.orm import exc

class garminhrfile():
    """ Plugin to import from a Garmin Training Center (version 1) file (as outputed from gpsbabel)
            Can have multiple activities in the file
            Checks to each activity to see if any entries are in the database with the same start time
            Creates GPX files for each activity not in the database

            Note: using lxml see http://codespeak.net/lxml
    """
    def __init__(self, parent = None, validate=False):
        self.parent = parent
        self.pytrainer_main = parent.pytrainer_main
        self.tmpdir = self.pytrainer_main.profile.tmpdir
        self.data_path = os.path.dirname(__file__)
        self.validate = validate
        self.sport = self.getConfValue("Force_sport_to")

    def getConfValue(self, confVar):
        info = XMLParser(self.data_path+"/conf.xml")
        code = info.getValue("pytrainer-plugin","plugincode")
        plugindir = self.pytrainer_main.profile.plugindir
        if not os.path.isfile(plugindir+"/"+code+"/conf.xml"):
            value = None
        else:
            info = XMLParser(plugindir+"/"+code+"/conf.xml")
            value = info.getValue("pytrainer-plugin",confVar)
        return value

    def run(self):
        logging.debug(">>")
        selectedFiles = fileChooserDialog(title="Choose a Garmin Training Center file to import").getFiles()
        guiFlush()
        importfiles = []
        if not selectedFiles:
            return importfiles
        for filename in selectedFiles: #could be multiple files selected - currently only single selection enabled
            if self.valid_input_file(filename):
                for (sport, tracks) in self.getTracks(filename):
                    logging.debug("Found %d tracks for %s sport in %s" % (len(tracks), sport, filename))
                    count = 0
                    for track in tracks: #can be multiple tracks
                        if self.shouldImport(track):
                            count += 1
                            gpxfile = "%s/garminhrfile%d.gpx" % (self.tmpdir, len(importfiles))
                            self.createGPXfile(gpxfile, track)
                            if self.sport: #Option to overide sport is set
                                importfiles.append((gpxfile, self.sport))
                            else: #Use sport from file
                                importfiles.append((gpxfile, sport))
                    logging.debug("Importing %d of %d tracks for sport %s" % (count, len(tracks), sport) )
            else:
                logging.info("File %s failed validation" % (filename))
        logging.debug("<<")
        return importfiles

    def valid_input_file(self, filename):
        """ Function to validate input file if requested"""
        if not self.validate: #not asked to validate
            logging.debug("Not validating %s" % (filename) )
            return True
        else: #Validate TCXv1, note are validating against gpsbabels 'broken' result...
            xslfile = os.path.realpath(self.pytrainer_main.data_path)+ "/schemas/GarminTrainingCenterDatabase_v1-gpsbabel.xsd"
            from lib.xmlValidation import xmlValidator
            validator = xmlValidator()
            return validator.validateXSL(filename, xslfile)

    def shouldImport(self, track):
        """ Function determines whether a track should be imported or not
                Currently using time only
        """
        timeElement = track.find(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v1}Time")
        if timeElement is None:
            #print (etree.tostring(track, pretty_print=True))
            logging.debug("Error no time found in track")
            return False
        else:
            time = timeElement.text
            try:
                self.pytrainer_main.ddbb.session.query(Activity).filter(Activity.date_time_utc == time).one()
                return False
            except exc.NoResultFound:
                return True

    def getTracks(self, filename):
        """ Function to return all the tracks in a Garmin Training Center v1 file
        """
        sportsList = ("Running", "Biking", "Other", "MultiSport")
        result = []
        tree = etree.ElementTree(file=filename)
        root = tree.getroot()
        for sport in sportsList:
            try:
                sportLevel = root.find(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v1}%s" % sport)
                tracks = sportLevel.findall(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v1}Track")
                result.append((sport, tracks))
            except:
                print("No entries for sport %s" % sport)
        return result

    def createGPXfile(self, gpxfile, track):
        """ Function to transform a Garmin Training Center v1 Track to a valid GPX+ file
        """
        xslt_doc = etree.parse(self.data_path+"/translate.xsl")
        transform = etree.XSLT(xslt_doc)
        result_tree = transform(track)
        result_tree.write(gpxfile, xml_declaration=True, encoding='UTF-8')
