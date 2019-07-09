# -*- coding: iso-8859-1 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net
# Modified by dgranda

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

import logging
import os
from lxml import etree

from pytrainer.lib.xmlUtils import XMLParser
from pytrainer.lib.date import getDateTime
from pytrainer.core.activity import Activity
from sqlalchemy.orm import exc

class garmintcxv1():
    def __init__(self, parent = None, data_path = None):
        logging.debug("init")
        self.parent = parent
        self.pytrainer_main = parent.parent
        self.tmpdir = self.pytrainer_main.profile.tmpdir
        self.main_data_path = data_path
        self.data_path = os.path.dirname(__file__)
        self.xmldoc = None
        self.activitiesSummary = []
        self.activities = []
        self.sportsList = ("Running", "Biking", "Other", "MultiSport")

    def getXmldoc(self):
        ''' Function to return parsed xmlfile '''
        return self.xmldoc

    def getFileType(self):
        return _("Garmin training center database file version 1")

    def getActivitiesSummary(self):
        return self.activitiesSummary

    def getDetails(self, activity, startTime):
        points = activity.findall(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v1}Trackpoint")
        while True:
            lastPoint = points[-1]
            try:
                time = lastPoint.find(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v1}Time")
                time = time.text
                break
            except:
                #Try again without the last point (i.e work from end until find time)
                points = points[:-1]
                continue
        return getDateTime(time)[0]-startTime[0]

    def testFile(self, filename):
        logging.debug('>>')
        logging.debug("Testing " + filename)
        try:
            #parse filename as xml
            xmldoc = etree.parse(filename)
            #Parse XML schema
            xmlschema_doc = etree.parse(self.main_data_path+"schemas/GarminTrainingCenterDatabase_v1-gpsbabel.xsd")
            xmlschema = etree.XMLSchema(xmlschema_doc)
            if (xmlschema.validate(xmldoc)):
                #Valid file
                self.xmldoc = xmldoc
                #Possibly multiple entries in file
                self.activities = self.getActivities(xmldoc)
                for (sport, activities) in self.activities:
                    logging.debug("Found %d tracks for %s sport in %s" % (len(activities), sport, filename))
                    for activity in activities:
                        startTime = getDateTime(self.getStartTimeFromActivity(activity))
                        inDatabase = self.inDatabase(activity, startTime)
                        duration  = self.getDetails(activity, startTime)
                        distance = ""
                        index = "%d:%d" % (self.activities.index((sport, activities)), activities.index(activity))
                        self.activitiesSummary.append( (index,
                                                                                        inDatabase,
                                                                                        startTime[1].strftime("%Y-%m-%dT%H:%M:%S"),
                                                                                        distance ,
                                                                                        str(duration),
                                                                                        sport,
                                                                                        ) )
                #print self.activitiesSummary
                return True
        except:
            #Not valid file
            return False
        return False

    def getActivities(self, tree):
        """ Function to return all the tracks in a Garmin Training Center v1 file
        """
        result = []
        root = tree.getroot()
        for sport in self.sportsList:
            try:
                sportLevel = root.find(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v1}%s" % sport)
                tracks = sportLevel.findall(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v1}Track")
                result.append((sport, tracks))
            except:
                print("No entries for sport %s" % sport)
        return result

    def inDatabase(self, activity, startTime):
        #comparing date and start time (sport may have been changed in DB after import)
        time = startTime
        if time is None:
            return False
        time = time[0].strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            self.parent.parent.ddbb.session.query(Activity).filter(Activity.date_time_utc == time).one()
            return True
        except exc.NoResultFound:
            return False

    def getStartTimeFromActivity(self, activity):
        timeElement = activity.find(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v1}Time")
        if timeElement is None:
            return None
        else:
            return timeElement.text

    def getGPXFile(self, ID, file_id):
        """
                Generate GPX file based on activity ID

                Returns (sport, GPX filename)
        """
        sport = None
        gpxFile = None
        #index = "%d:%d" % (self.activities.index((sport, activities)), activities.index(activity))
        sportID, activityID = ID.split(':')
        sportID = int(sportID)
        activityID = int(activityID)
        sport, activities = self.activities[sportID]
        activitiesCount = len(self.activities)
        if activitiesCount > 0 and activityID < activitiesCount:
            gpxFile = "%s/garmin-tcxv1-%s-%d.gpx" % (self.tmpdir, file_id, activityID)
            activity = activities[activityID]
            self.createGPXfile(gpxFile, activity)
        return sport, gpxFile

    def createGPXfile(self, gpxfile, activity):
        """ Function to transform a Garmin Training Center v2 Track to a valid GPX+ file
        """
        xslt_doc = etree.parse(self.data_path+"/translate_garmintcxv1.xsl")
        transform = etree.XSLT(xslt_doc)
        #xml_doc = etree.parse(filename)
        xml_doc = activity
        result_tree = transform(xml_doc)
        result_tree.write(gpxfile, xml_declaration=True, encoding='UTF-8')
