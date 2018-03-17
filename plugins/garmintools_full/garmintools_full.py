#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net

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

# Added to support python installations older than 2.6
from __future__ import with_statement

import os
import sys
import logging
import fnmatch
import commands
from io import BytesIO
import traceback
import dateutil.parser

from lxml import etree
from pytrainer.lib.xmlUtils import XMLParser
from datetime import date, timedelta, datetime
from dateutil.tz import * # for tzutc()
from pytrainer.core.activity import Activity

class garmintools_full():
    """ Plugin to import from a Garmin device using garmintools
            Checks each activity to see if any entries are in the database with the same start time
            Creates GPX files for each activity not in the database

            Note: using lxml see http://codespeak.net/lxml
    """
    def __init__(self, parent = None, validate=False):
        self.parent = parent
        self.pytrainer_main = parent.pytrainer_main
        self.confdir = self.pytrainer_main.profile.confdir
        self.tmpdir = self.pytrainer_main.profile.tmpdir
        # Tell garmintools where to save retrieved data from GPS device
        os.environ['GARMIN_SAVE_RUNS']=self.tmpdir
        self.data_path = os.path.dirname(__file__)
        self.validate = validate
        self.sport = self.getConfValue("Force_sport_to")
        self.deltaDays = self.getConfValue("Not_older_days")
        if self.deltaDays is None:
            logging.info("Delta days not set, retrieving complete history, defaulting to 0")
            self.deltaDays = 0
        #so far hardcoded to False - dg 20100104
        #self.legacyComp = self.getConfValue("Legacy_comparison")
        self.maxGap = self.getConfValue("Max_gap_seconds")
        if self.maxGap is None:
            logging.info("No gap defined, strict comparison")
            self.maxGap = 0

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
        importFiles = []
        if self.checkLoadedModule():
            numError = self.getDeviceInfo()
            if numError >= 0:
                #TODO Remove Zenity below
                outgps = commands.getstatusoutput("garmin_save_runs -v| zenity --progress --pulsate --text='Loading Data' --auto-close")
                if outgps[0]==0:
                    # now we should have a lot of gmn (binary) files under $GARMIN_SAVE_RUNS
                    foundFiles = self.searchFiles(self.tmpdir, "gmn")
                    logging.info("Retrieved "+str(len(foundFiles))+" entries from GPS device")
                    # Trying to minimize number of files to dump
                    if int(self.deltaDays) > 0:
                        selectedFiles = self.discardOld(foundFiles)
                    else:
                        logging.info("Retrieving complete history from GPS device")
                        selectedFiles = foundFiles
                    if len(selectedFiles) > 0:
                        logging.info("Dumping "+str(len(selectedFiles))+" binary files found")
                        dumpFiles = self.dumpBinaries(selectedFiles)
                        self.listStringDBUTC = self.pytrainer_main.ddbb.session.query(Activity)
                        if self.maxGap > 0:
                            logging.info("Starting import. Comparison will be made with "+str(self.maxGap)+" seconds interval")
                        else:
                            logging.info("Starting import. Comparison will be strict")
                        importFiles = self.importEntries(dumpFiles)
                    else:
                        logging.info("No new entries to add")
                else:
                    logging.error("Error when retrieving data from GPS device")
            else:
                #TODO Remove Zenity below
                if numError == -1:
                    os.popen("zenity --error --text='No Garmin device found\nCheck your configuration'");
                elif numError == -2:
                    os.popen("zenity --error --text='Can not find garmintools binaries\nCheck your configuration'")
        else: #No garmin device found
                #TODO Remove Zenity below
            os.popen("zenity --error --text='Can not handle Garmin device (wrong module loaded)\nCheck your configuration'");
        logging.info("Entries to import: "+str(len(importFiles)))
        logging.debug("<<")
        return importFiles

    def discardOld(self, listEntries):
        logging.debug(">>")
        tempList = []
        logging.info("Discarding entries older than "+str(self.deltaDays)+" days")
        limit = datetime.now() - timedelta(days = int(self.deltaDays))
        for entry in listEntries:
            filename = os.path.split(entry)[1].rstrip(".gmn")
            filenameDateTime = datetime.strptime(filename,"%Y%m%dT%H%M%S")
            logging.debug("Entry time: "+str(filenameDateTime)+" | limit: "+str(limit))
            if filenameDateTime < limit:
                logging.debug("Discarding old entry: "+str(filenameDateTime))
            else:
                tempList.append(entry)
        logging.debug("<<")
        return tempList

    def importEntries(self, entries):
        # modified from garmintools plugin written by jb
        logging.debug(">>")
        logging.debug("Selected files: "+str(entries))
        importfiles = []
        for filename in entries:
            if self.valid_input_file(filename):
                #Garmin dump files are not valid xml - need to load into a xmltree
                #read file into string
                with open(filename, 'r') as f:
                    xmlString = f.read()
                # Double check encoding from dump files. ASCII?
                fileString = BytesIO(b"<root>" + xmlString + b"</root>")
                #parse string as xml
                try:
                    tree = etree.parse(fileString)
                    #if not self.inDatabase(tree, filename):
                    if not self.entryExists(tree, filename):
                        sport = self.getSport(tree)
                        gpxfile = "%s/garmintools-%d.gpx" % (self.tmpdir, len(importfiles))
                        self.createGPXfile(gpxfile, tree)
                        importfiles.append((gpxfile, sport))
                    else:
                        logging.debug("%s already present. Skipping import." % (filename,) )
                except:
                    logging.error('Error parsing entry '+ str(filename))
                    traceback.print_exc()
            else:
                logging.error("File %s failed validation" % (filename))
        logging.debug("<<")
        return importfiles

    def valid_input_file(self, filename):
        """ Function to validate input file if requested"""
        if not self.validate:  #not asked to validate
            logging.debug("Not validating %s" % (filename) )
            return True
        else:
            logging.debug("Cannot validate garmintools dump files yet")
            return True
            '''xslfile = os.path.realpath(self.parent.parent.data_path)+ "/schemas/GarminTrainingCenterDatabase_v2.xsd"
            from lib.xmlValidation import xmlValidator
            validator = xmlValidator()
            return validator.validateXSL(filename, xslfile)'''

    def entryExists(self, tree, filename):
        logging.debug(">>")
        stringStartDatetime = self.detailsFromFile(tree) # this time is localtime! (with timezone offset)
        exists = False
        if stringStartDatetime is not None:
            startDatetime = dateutil.parser.parse(stringStartDatetime)
            # converting to utc for proper comparison with date_time_utc
            stringStartUTC = startDatetime.astimezone(tzutc()).strftime("%Y-%m-%dT%H:%M:%SZ")
            if self.checkDupe(stringStartUTC, self.listStringDBUTC, int(self.maxGap)):
                exists = True
            else:
                logging.info("Marking "+str(filename)+" | "+str(stringStartUTC)+" to import")
                exists = False
        else:
            logging.debug("Not able to find start time, please check "+str(filename))
            exists = True # workaround for old/not correct entries (will crash at some point during import process otherwise)
        logging.debug("<<")
        return exists

    def checkDupe(self, stringStartUTC, listStringStartUTC, gap):
        """ Checks if there is any startUTC in DB between provided startUTC plus a defined gap:
                Check for same day (as baselined to UTC)
                startDatetime + delta (~ 3 mins) >= listDatetime[x]
                args:
                        stringStartUTC
                        listStringStartUTC
                        gap
                returns: True if any coincidence is found. False otherwise"""
        logging.debug(">>")
        found = False
        if gap > 0:
            # Retrieve date from 2010-01-14T11:34:49Z
            stringStartDate = stringStartUTC[0:10]
            for entry in listStringStartUTC:
                #logging.debug("start: "+str(startDatetime)+" | entry: "+str(entry)+" | gap: "+str(datetimePlusDelta))
                if entry.date_time_utc.startswith(stringStartDate):
                    deltaGap = timedelta(seconds=gap)
                    datetimeStartUTC = datetime.strptime(stringStartUTC,"%Y-%m-%dT%H:%M:%SZ")
                    datetimeStartUTCDB = datetime.strptime(entry.date_time_utc, "%Y-%m-%dT%H:%M:%SZ")
                    datetimePlusDelta = datetimeStartUTC + deltaGap
                    if datetimeStartUTC <= datetimeStartUTCDB and datetimeStartUTCDB <= datetimePlusDelta:
                        found = True
                        logging.debug("Found: "+str(stringStartUTC)+" <= "+entry.date_time_utc+" <= "+str(datetimePlusDelta))
                        break
        else:
            if (stringStartUTC,) in listStringStartUTC: # strange way to store results from DB
                found = True
        logging.debug("<<")
        return found

    def getSport(self, tree):
        #return sport from file or overide if present
        if self.sport:
            return self.sport
        root = tree.getroot()
        sportElement = root.find(".//run")
        try:
            sport = sportElement.get("sport")
            sport = sport.capitalize()
        except:
            sport = "import"
        return sport

    def detailsFromFile(self, tree):
        root = tree.getroot()
        #Find first point
        pointElement = root.find(".//point")
        if pointElement is not None:
            stringStartDatetime = pointElement.get("time")
            return stringStartDatetime
        return None

    def createGPXfile(self, gpxfile, tree):
        """ Function to transform a Garmintools dump file to a valid GPX+ file
        """
        xslt_doc = etree.parse(self.data_path+"/translate.xsl")
        transform = etree.XSLT(xslt_doc)
        result_tree = transform(tree)
        result_tree.write(gpxfile, xml_declaration=True, encoding='UTF-8')

    def dumpBinaries(self, listFiles):
        logging.debug(">>")
        dumpFiles=[]
        for filename in listFiles:
            outdump = filename.replace('.gmn', '.dump')
            logging.debug("outdump: "+str(outdump))
            result = commands.getstatusoutput("garmin_dump %s > %s" %(filename,outdump))
            if result[0] == 0:
                dumpFiles.append(outdump)
            else:
                logging.error("Error when creating dump of "+str(filename)+": "+str(result))
        logging.debug("<<")
        return dumpFiles

    def searchFiles(self, rootPath, extension):
        logging.debug(">>")
        foundFiles=[]
        logging.debug("rootPath: "+str(rootPath))
        result = commands.getstatusoutput("find %s -name *.%s" %(rootPath,extension))
        if result[0] == 0:
            foundFiles = result[1].splitlines()
            #logging.debug("Found files: "+str(foundFiles))
            logging.info ("Found files: "+str(len(foundFiles)))
        else:
            logging.error("Not able to locate files from GPS: "+str(result))
        logging.debug("<<")
        return foundFiles

    def getDeviceInfo(self):
        logging.debug(">>")
        result = commands.getstatusoutput('garmin_get_info')
        logging.debug("Returns "+str(result))
        numError = 0
        if result[0] == 0:
            if result[1] != "garmin unit could not be opened!":
                try:
                    xmlString = result[1].rstrip()
                    xmlString_2 = ' '.join(xmlString.split())
                    tree = etree.fromstring(xmlString_2)
                    description = self.getProductDesc(tree)
                    if description is not None:
                        logging.info("Found "+str(description))
                    else:
                        raise Exception
                except:
                    logging.error("Not able to identify GPS device. Continuing anyway...")
                    logging.debug("Traceback: %s" % traceback.format_exc())
                    pass
            else:
                logging.error(result[1])
                numError = -1
        else:
            logging.error("Can not find garmintools binaries, please check your installation")
            numError = -2
        logging.debug("<<")
        return numError

    def getProductDesc(self, tree):
        desc = tree.findtext(".//product_description")
        return desc

    def checkLoadedModule(self):
        try:
            outmod = commands.getstatusoutput('/sbin/lsmod | grep garmin_gps')
            if outmod[0]==256:      #there is no garmin_gps module loaded
                return True
            else:
                return False
        except:
            return False

    def createUserdirBackup(self):
        logging.debug('>>')
        result = commands.getstatusoutput('tar -cvzf '+os.environ['HOME']+'/pytrainer_`date +%Y%m%d_%H%M`.tar.gz '+self.confdir)
        if result[0] != 0:
            raise Exception, "Copying current user directory does not work, error #"+str(result)
        else:
            logging.info('User directory backup successfully created')
        logging.debug('<<')
