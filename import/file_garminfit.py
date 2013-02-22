#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import traceback
import subprocess
from lxml import etree
from pytrainer.lib.date import Date
from pytrainer.lib.xmlUtils import XMLParser

class garminfit():
    '''First approach to parse Garmin FIT files is to use perl scripts (http://pub.ks-and-ks.ne.jp/cycling/fit2tcx.shtml) from Kiyokazu SUTO (suto@ks-and-ks.ne.jp) to convert first to TCXv2 and then to GPX+ format.
        Another step would be to use other parsers like GPSBabel (http://www.gpsbabel.org/htmldoc-1.4.3/fmt_garmin_fit.html) and python-fitparse (https://github.com/dtcooper/python-fitparse)
     '''
    def __init__(self, parent = None, data_path = None):
        self.parent = parent
        self.pytrainer_main = parent.parent
        self.tmpdir = self.pytrainer_main.profile.tmpdir
        self.main_data_path = data_path
        self.data_path = os.path.dirname(__file__)
        self.xmldoc = None
        self.activitiesSummary = []
        self.activities = []

    def getXmldoc(self):
        ''' Function to return parsed xmlfile '''
        return self.xmldoc

    def getFileType(self):
        return "Garmin Flexible and Interoperable data Transfer (FIT)"

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
            logging.debug("Activity distance (m): %s | duration (hh:mm:ss): %s" % (distance, duration_hhmmss))
        logging.debug("<<")
        return float(distance), duration_hhmmss

    def fromFIT2TCXv2 (self, filename):
        ''' Reads binary fit file and returns xml string in TCXv2 format'''
        logging.debug(">>")
        result = False
        try:
            pipe = subprocess.Popen(["perl", self.main_data_path+"plugins/garmin-fit/bin/fit2tcx", filename], stdout=subprocess.PIPE)
            result = pipe.stdout.read()
        except:
            logging.debug("Traceback: %s" % traceback.format_exc())
        logging.debug("<<")
        return result

    def testFile(self, filename):
        logging.debug('>>')
        logging.debug("Testing " + filename)
        try:
            # Original file is in fit format, so first it will be translated into tcxv2 and then parsed
            xmldoc = etree.fromstring(self.fromFIT2TCXv2(filename))
            #Parse XML schema
            xmlschema_doc = etree.parse(self.main_data_path+"schemas/GarminTrainingCenterDatabase_v2.xsd")
            xmlschema = etree.XMLSchema(xmlschema_doc)
            if (xmlschema.validate(xmldoc)):
                logging.debug("FIT file converted to valid TCXv2")
                self.xmldoc = xmldoc
                #Possibly multiple entries in file
                self.activities = self.getActivities(xmldoc)
                for activity in self.activities:
                    startTime = self.getDateTime(self.getStartTimeFromActivity(activity))
                    inDatabase = self.inDatabase(activity, startTime)
                    sport = self.getSport(activity)
                    distance, duration  = self.getDetails(activity, startTime)
                    distance = distance / 1000.0
                    self.activitiesSummary.append( (self.activities.index(activity),
                                                                 inDatabase, 
                                                                 startTime[1].strftime("%Y-%m-%dT%H:%M:%S"), 
                                                                 "%0.2f" % distance , 
                                                                 str(duration), 
                                                                 sport,
                                                                 ) )
                    return True
        except:
            logging.debug("Traceback: %s" % traceback.format_exc())
            return False 
        return False

    def getActivities(self, tree):
        '''Function to return all activities in Garmin training center version 2 file
        '''
        #root = tree.getroot()
        #fromstring() parses XML from a string directly into an Element, which is the root element of the parsed tree.
        activities = tree.findall(".//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Activity")
        return activities

    def inDatabase(self, activity, startTime):
        #comparing date and start time (sport may have been changed in DB after import)
        time = startTime
        if time is None:
            return False
        time = time[0].strftime("%Y-%m-%dT%H:%M:%SZ")
        if self.parent.parent.ddbb.select("records","*","date_time_utc=\"%s\"" % (time)):
            return True
        else:
            return False

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
        """
               Generate GPX file based on activity ID

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
        """ Function to transform a Garmin Training Center v2 Track to a valid GPX+ file
        """
        xslt_doc = etree.parse(self.data_path+"/translate_garmintcxv2.xsl")
        transform = etree.XSLT(xslt_doc)
        #xml_doc = etree.parse(filename)
        xml_doc = activity
        result_tree = transform(xml_doc)
        result_tree.write(gpxfile, xml_declaration=True, encoding='UTF-8')

