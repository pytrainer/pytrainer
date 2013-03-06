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
import traceback
from lxml import etree
from pytrainer.lib.date import Date

from pytrainer.lib.xmlUtils import XMLParser

class garmintcxv2():
    def __init__(self, parent = None, data_path = None):
        if parent is not None:
            self.parent = parent
            self.pytrainer_main = parent.parent
            self.tmpdir = self.pytrainer_main.profile.tmpdir
        if data_path is not None:
            self.main_data_path = data_path
            self.data_path = os.path.dirname(__file__)
        self.xmldoc = None
        self.activitiesSummary = []
        self.activities = []

    def getXmldoc(self):
        ''' Function to return parsed xmlfile '''
        return self.xmldoc

    def getFileType(self):
        return _("Garmin training center database file version 2")

    def getActivitiesSummary(self):
        return self.activitiesSummary

    def getDetails(self, activity, startTime):
        logging.debug(">>")
        distance = 0
        duration = 0
        laps = activity.findall(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Lap")
        if laps:
            for lap in laps:
                lap_duration = float(lap.findtext(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}TotalTimeSeconds"))
                lap_distance = float(lap.findtext(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}DistanceMeters"))
                logging.debug("Lap distance (m): %f | duration (s): %f" % (lap_distance, lap_duration))
                distance += lap_distance
                duration += lap_duration
            hours = int(duration)//3600
            minutes = (int(duration)/60)%60
            seconds = int(duration)%60
            duration_hhmmss = "%02d:%02d:%02d" % (hours, minutes, seconds)       
            logging.debug("Activity distance (m): %f | duration (hh:mm:ss - s): %s - %f" % (distance, duration_hhmmss, duration))
        else:
            points = activity.findall(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint")
            while True:
                lastPoint = points[-1]
                try:
                    distance = lastPoint.find(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}DistanceMeters")
                    if distance is None:
                        points = points[:-1]
                        continue
                    time = lastPoint.find(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Time")
                    distance = distance.text
                    time = time.text
                    break
                except:
                    #Try again without the last point (i.e work from end until find time and distance)
                    points = points[:-1]
                    continue
            duration_hhmmss = self.getDateTime(time)[0]-startTime[0]
            logging.debug("Activity distance (m): %f | duration (hh:mm:ss): %s" % (distance, duration_hhmmss))
        logging.debug("<<")
        return float(distance), duration_hhmmss

    def validate(self, xmldoc, schema):
        logging.debug(">>")
        xmlschema_doc = etree.parse(self.main_data_path + schema)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        logging.debug("<<")
        return xmlschema.validate(xmldoc)

    def buildActivitiesSummary(self):
        logging.debug(">>")
        self.activities = self.getActivities()
        for activity in self.activities:
            startTime = self.getDateTime(self.getStartTimeFromActivity(activity))
            inDatabase = self.inDatabase(startTime)
            sport = self.getSport(activity)
            distance, duration  = self.getDetails(activity, startTime)
            distance = distance / 1000.0
            self.activitiesSummary.append((self.activities.index(activity),
                                                                 inDatabase, 
                                                                 startTime[1].strftime("%Y-%m-%dT%H:%M:%S"), 
                                                                 "%0.2f" % distance , 
                                                                 str(duration), 
                                                                 sport,
                                                                 ))
        print self.activitiesSummary
        logging.debug("<<")

    def testFile(self, filename):
        '''Check if file is valid TCXv2 one and if yes, retrieve activities from it'''
        logging.debug('>>')
        logging.debug("Testing %s" %filename)
        result = False
        try:
            xmldoc = etree.parse(filename)
            valid_xml = self.validate(xmldoc, "schemas/GarminTrainingCenterDatabase_v2.xsd")
            if (valid_xml):
                logging.debug("Valid TCXv2 file (%s)" %filename)
                self.xmldoc = xmldoc
                self.buildActivitiesSummary()
                result = True
        except:
            logging.debug("Traceback: %s" % traceback.format_exc())
        logging.debug('<<')
        return result

    def getActivities(self):
        '''Function to return all activities in Garmin training center version 2 file'''
        logging.debug('>>')
        activities = self.xmldoc.findall(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Activity")
        logging.debug('<<')
        return activities

    def inDatabase(self, startTime):
        #comparing date and start time (sport may have been changed in DB after import)
        logging.debug('>>')
        result = False
        if startTime is not None:
            logging.info("Checking if activity from %s exists in db" % startTime[0]) # 2012-10-14 10:02:42+00:00
            time = startTime[0].strftime("%Y-%m-%dT%H:%M:%SZ")
            if self.parent.parent.ddbb.select("records","*","date_time_utc=\"%s\"" % (time)):
                result = True
        else:
            logging.info("No start time provided, nothing to check")
        logging.debug('<<')
        return result

    def getSport(self, activity):
        try:
            sport = activity.get("Sport")
        except:
            sport = "import"
        return sport

    def getStartTimeFromActivity(self, activity):
        timeElement = activity.find(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Id")
        if timeElement is None:
            return None
        else:
            return timeElement.text

    def getDateTime(self, time_):
        return Date().getDateTime(time_)

    def getGPXFile(self, ID, file_id):
        """ Generate GPX file based on activity ID
            Returns (sport, GPX filename)
        """
        sport = None
        gpxFile = None
        activityID = int(ID)
        activitiesCount = len(self.activities)
        if activitiesCount > 0 and activityID < activitiesCount:
            gpxFile = "%s/garmin-tcxv2-%s-%d.gpx" % (self.tmpdir, file_id, activityID)
            activity = self.activities[int(activityID)]
            sport = self.getSport(activity)
            self.createGPXfile(gpxFile, activity)
        return sport, gpxFile  

    def createGPXfile(self, gpxfile, activity):
        """ Function to transform a Garmin Training Center v2 Track to a valid GPX+ file"""
        xslt_doc = etree.parse(self.data_path+"/translate_garmintcxv2.xsl")
        transform = etree.XSLT(xslt_doc)
        xml_doc = activity
        result_tree = transform(xml_doc)
        result_tree.write(gpxfile, xml_declaration=True, encoding='UTF-8')

