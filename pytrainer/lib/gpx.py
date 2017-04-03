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

import sys
import string
import math
import re
import os

import time
from datetime import datetime
import logging
from lxml import etree
from pytrainer.lib.date import getDateTime

# use of namespaces is mandatory if defined
mainNS = string.Template(".//{http://www.topografix.com/GPX/1/1}$tag")
timeTag = mainNS.substitute(tag="time")
trackTag = mainNS.substitute(tag="trk")
trackPointTag = mainNS.substitute(tag="trkpt")
trackPointTagLast = mainNS.substitute(tag="trkpt[last()]")
trackSegTag = mainNS.substitute(tag="trkseg")
elevationTag = mainNS.substitute(tag="ele")
nameTag = mainNS.substitute(tag="name")

gpxdataNS = string.Template(".//{http://www.cluetrust.com/XML/GPXDATA/1/0}$tag")
calorieTag = gpxdataNS.substitute(tag="calories")
hrTag = gpxdataNS.substitute(tag="hr")
cadTag = gpxdataNS.substitute(tag="cadence")
lapTag = gpxdataNS.substitute(tag="lap")
endPointTag = gpxdataNS.substitute(tag="endPoint")
startPointTag = gpxdataNS.substitute(tag="startPoint")
elapsedTimeTag = gpxdataNS.substitute(tag="elapsedTime")
distanceTag = gpxdataNS.substitute(tag="distance")
intensityTag = gpxdataNS.substitute(tag="intensity")
triggerTag = gpxdataNS.substitute(tag="trigger")
summaryTag = gpxdataNS.substitute(tag="summary")

pytrainerNS = string.Template(".//{http://sourceforge.net/projects/pytrainer/GPX/0/1}$tag")
pyt_eleTag = pytrainerNS.substitute(tag="ele")

class Gpx:
    def __init__(self, data_path = None, filename = None, trkname = None):
        logging.debug(">>")
        #print("GPX init-ing")
        global mainNS, timeTag, trackTag, trackPointTag, trackPointTagLast, trackSegTag, elevationTag, nameTag
        self.data_path = data_path
        self.filename = filename
        self.trkname = trkname
        logging.debug(str(data_path)+"|"+str(filename)+"|"+str(trkname))
        self.trkpoints = []
        self.vel_array = []
        self.total_dist = 0
        self.total_dist_trkpts = 0
        self.total_time = 0
        self.total_time_trkpts = 0
        self.upositive = 0
        self.unegative = 0
        self.maxvel = 0
        self.maxhr = 0
        self.hr_average = 0
        self.date = ""
        self.start_time = ""
        self.calories= 0
        self.tree = None
        if filename != None:
            if not os.path.isfile(self.filename):
                return None
            logging.debug("parsing content from "+self.filename)
            self.tree = etree.ElementTree(file=filename).getroot()
            if self.tree.get("version") == "1.0":
                #Got an old GPX file
                logging.debug("Old gpx version")
                mainNS = string.Template(".//{http://www.topografix.com/GPX/1/0}$tag")
                timeTag = mainNS.substitute(tag="time")
                trackTag = mainNS.substitute(tag="trk")
                trackPointTag = mainNS.substitute(tag="trkpt")
                trackPointTagLast = mainNS.substitute(tag="trkpt[last()]")
                trackSegTag = mainNS.substitute(tag="trkseg")
                elevationTag = mainNS.substitute(tag="ele")
                nameTag = mainNS.substitute(tag="name")
            else:
                logging.debug("Importing version %s gpx file" % self.tree.get("version"))
                mainNS = string.Template(".//{http://www.topografix.com/GPX/1/1}$tag")
                timeTag = mainNS.substitute(tag="time")
                trackTag = mainNS.substitute(tag="trk")
                trackPointTag = mainNS.substitute(tag="trkpt")
                trackPointTagLast = mainNS.substitute(tag="trkpt[last()]")
                trackSegTag = mainNS.substitute(tag="trkseg")
                elevationTag = mainNS.substitute(tag="ele")
                nameTag = mainNS.substitute(tag="name")
                intensityTag = mainNS.substitute(tag="intensity")

            logging.debug("getting values...")
            self.Values = self._getValues()
        logging.debug("<<")

    def getMaxValues(self):
        return self.total_dist, self.total_time, self.maxvel, self.maxhr

    def getDate(self):
        return self.date

    def getTrackRoutes(self):
        trks = self.tree.findall(trackTag)
        tracks = []
        retorno = []
        for trk in trks:
            nameResult = trk.find(nameTag)
            if nameResult is not None:
                name = nameResult.text
            else:
                name = _("No Name")
            timeResult = trk.find(timeTag)
            if timeResult is not None:
                time_ = timeResult.text # check timezone
                logging.debug("TimeResult: %s" %time_)
                mk_time = getDateTime(time_)[0]
                time_ = mk_time.strftime("%Y-%m-%d")
            else:
                time_ = _("No Data")
            logging.debug("name: "+name+" | time: "+time_)
            tracks.append((name,time_))
        return tracks

    def getUnevenness(self):
        return self.upositive,self.unegative

    def getTrackList(self):
        return self.Values

    def getHeartRateAverage(self):
        return self.hr_average

    def getCalories(self):
        return self.calories

    def getStart_time(self):
        return self.start_time

    def getLaps(self):
        logging.debug(">>")
        lapInfo = []
        if self.tree is None:
            return lapInfo
        tree  = self.tree
        laps = tree.findall(lapTag)
        logging.debug("Found %d laps" % len(laps))
        if len(laps) == 0:
            #Found no laps, so add single lap with totals
            stLat = self.trkpoints[0]['lat']
            stLon = self.trkpoints[0]['lon']
            lat = self.trkpoints[-1]['lat']
            lon = self.trkpoints[-1]['lon']
            logging.debug("total_time: %s" %self.total_time)
            lapInfo.append((self.total_time, lat, lon, self.calories, self.total_dist*1000, stLat, stLon, "active", self.hr_average, self.maxhr, self.maxvel, "manual"))
        else:
            for lap in laps:
                endPoint = lap.find(endPointTag)
                lat = endPoint.get("lat")
                lon = endPoint.get("lon")
                startPoint = lap.find(startPointTag)
                if startPoint is not None:
                    stLat = startPoint.get("lat")
                    stLon = startPoint.get("lon")
                else:
                    stLat, stLon = "",""
                elapsedTime = lap.findtext(elapsedTimeTag)
                if elapsedTime.count(":") == 2: # got a 0:41:42.14 type elasped time
                    hours, mins, secs = elapsedTime.split(":")
                    elapsedTime = str((int(hours) *3600) + (int(mins) * 60) + float(secs))
                calories = lap.findtext(calorieTag)
                distance = lap.findtext(distanceTag)
                logging.info("Found time: %s, start lat: %s, start lon: %s, end lat: %s end lon: %s cal: %s dist: %s " % (elapsedTime, stLat, stLon, lat, lon, calories, distance))
                intensity = lap.findtext(intensityTag).lower()
                trigger_element = lap.find(triggerTag)
                #logging.debug("Trigger element: %s" % etree.tostring(trigger_element))
                if "kind" in trigger_element.keys():
                    trigger = trigger_element.get("kind").lower()
                else:
                    trigger = trigger_element.text.lower()
                # attribute xpath features are only available in 1.3 (python >= 2.7) - 2012/01/28 - dgranda
                lap_summary = lap.findall(summaryTag)
                num_elements = len(lap_summary)
                summary_dict = {"MaximumSpeed": 0,
                                "AverageHeartRateBpm": None,
                                "MaximumHeartRateBpm": None}
                if num_elements > 0:
                    if num_elements == 1: # old _non compliant_ pytrainer estructure
                        #logging.debug("lap_summary[0]: %s" % etree.tostring(lap_summary[0]))
                        for key in summary_dict.keys():
                            summary_dict[key] = lap_summary[0].findtext(mainNS.substitute(tag=key))
                            logging.debug("%s: %s" % (key, summary_dict[key]))
                    else:
                        for summary_element in lap_summary:
                            summary_dict[summary_element.get('name')] = summary_element.text
                            logging.debug("%s: %s" % (summary_element.get('name'), summary_element.text))
                    max_speed = summary_dict["MaximumSpeed"]
                    avg_hr = summary_dict["AverageHeartRateBpm"]
                    max_hr = summary_dict["MaximumHeartRateBpm"]
                else:
                    logging.info("No summary found")
                logging.info("Intensity: %s | Trigger: %s | Max speed: %s | Average hr: %s | Maximum hr: %s" % (intensity, trigger, max_speed, avg_hr, max_hr))
                lapInfo.append((elapsedTime, lat, lon, calories, distance, stLat, stLon, intensity, avg_hr, max_hr, max_speed, trigger))
        logging.debug("<<")
        return lapInfo

    def _getValues(self):
        '''
        Migrated to eTree XML processing 26 Nov 2009 - jblance
        '''
        logging.debug(">>")
        tree  = self.tree
        # Calories data comes within laps. Maybe more than one, adding them together - dgranda 20100114
        # Distance data comes within laps where present as well - dgranda 20110204
        laps = tree.findall(lapTag)
        if laps is not None and laps != "":
            totalDistance = 0
            totalDuration = 0
            for lap in laps:
                lapCalories = lap.findtext(calorieTag)                
                self.calories += int(lapCalories)
                lapDistance = lap.findtext(distanceTag)
                totalDistance += float(lapDistance)
                lapDuration_tmp = lap.findtext(elapsedTimeTag)
                # When retrieving data from TCX file -> seconds (float)
                # When retrieving data from GPX+ file -> hh:mm:ss
                # EAFP -> http://docs.python.org/glossary.html
                try:
                    lapDuration = float(lapDuration_tmp)
                except ValueError:
                    hour,minu,sec = lapDuration_tmp.split(":")
                    lapDuration = float(sec) + int(minu)*60 + int(hour)*3600
                totalDuration += lapDuration 
                logging.info("Lap distance: %s m | Duration: %s s | Calories: %s kcal" % (lapDistance, lapDuration, lapCalories))
            self.total_dist = float(totalDistance/1000.0) # Returning km
            self.total_time = int(totalDuration) # Returning seconds
            logging.info("Laps - Distance: %.02f km | Duration: %d s | Calories: %s kcal" % (self.total_dist, self.total_time, self.calories))
        else:
            laps = []

        retorno = []
        his_vel = []
        last_lat = None
        last_lon = None
        last_time = None
        total_dist = 0
        dist_elapsed = 0 # distance since the last time found
        total_hr = 0
        tmp_alt = 0
        len_validhrpoints = 0
        trkpoints = tree.findall(trackPointTag)
        if trkpoints is None or len(trkpoints) == 0:
            logging.debug( "No trkpoints found in file")
            return retorno
        logging.debug("%d trkpoints in file" % len(trkpoints))

        date_ = tree.find(timeTag).text
        if date_ is None:
            logging.info("time tag is blank")
            self.date = None
        else:
            mk_time = getDateTime(date_)[1] #Local Date
            self.date = mk_time.strftime("%Y-%m-%d")
            self.start_time = mk_time.strftime("%H:%M:%S")
        waiting_points = []
        logging.debug("date: %s | start_time: %s | mk_time: %s" % (self.date, self.start_time, mk_time))

        for i, trkpoint in enumerate(trkpoints):
            #Get data from trkpoint
            try:
                lat = float(trkpoint.get("lat"))
                lon = float(trkpoint.get("lon"))
            except Exception as e:
                logging.debug(str(e))
                lat = lon = None
            if lat is None or lat == "" or lat == 0 or lon is None or lon == "" or lon == 0:
                logging.debug("lat or lon is blank or zero")
                continue
            #get the heart rate value from the gpx extended format file
            hrResult = trkpoint.find(hrTag)
            if hrResult is not None:
                hr = int(hrResult.text)
                len_validhrpoints += 1
                total_hr += hr          #TODO fix
                if hr>self.maxhr:
                    self.maxhr = hr
            else:
                hr = None
            #get the cadence (if present)
            cadResult = trkpoint.find(cadTag)
            if cadResult is not None:
                cadence = int(cadResult.text)
            else:
                cadence = None

            #get the time
            timeResult = trkpoint.find(timeTag)
            if timeResult is not None:
                date_ = timeResult.text
                mk_time = getDateTime(date_)[0]
                time_ = time.mktime(mk_time.timetuple()) #Convert date to seconds
                if i == 0:
                    time_elapsed = 0
                else:
                    time_elapsed = time_ - self.trkpoints[i-1]['time'] if self.trkpoints[i-1]['time'] is not None else 0
                    if time_elapsed > 10:
                        logging.debug("%d seconds from last trkpt, someone took a break!" % time_elapsed)
                        # Calculating average lapse between trackpoints to add it
                        average_lapse = round(self.total_time_trkpts/i)
                        logging.debug("Adding %d seconds (activity average) as lapse from last point" % average_lapse)
                        self.total_time_trkpts += average_lapse
                    else:
                        self.total_time_trkpts += time_elapsed
            else:
                time_ = None
                time_elapsed = None

            #get the elevation
            eleResult = trkpoint.find(elevationTag)
            rel_alt = 0
            if eleResult is not None:
                try:
                    ele = float(eleResult.text)
                    #Calculate elevation change
                    if i != 0:
                        rel_alt = ele - self.trkpoints[i-1]['ele'] if self.trkpoints[i-1]['ele'] is not None else 0
                except Exception as e:
                    logging.debug(str(e))
                    ele = None
            else:
                ele = None
                
            #Get corrected elevation if it exists
            correctedEleResult = trkpoint.find(pyt_eleTag)
            if correctedEleResult is not None:
                try:
                    corEle = float(correctedEleResult.text)
                    #Calculate elevation change
                except Exception as e:
                    logging.debug(str(e))
                    corEle = None
            else:
                corEle = None

            #Calculate climb or decent amount
            #Allow for some 'jitter' in height here
            JITTER_VALUE = 0  #Elevation changes less than this value are not counted in +-
            if abs(rel_alt) < JITTER_VALUE:
                rel_alt = 0
            if rel_alt > 0:
                self.upositive += rel_alt
            elif rel_alt < 0:
                self.unegative -= rel_alt

            #Calculate distance between two points
            if i == 0: #First point
                dist = None
            else:
                dist = self._distance_between_points(lat1=self.trkpoints[i-1]['lat'], lon1=self.trkpoints[i-1]['lon'], lat2=lat, lon2=lon)

            #Accumulate distances
            if dist is not None:
                dist_elapsed += dist #TODO fix
                self.total_dist_trkpts += dist

            #Calculate speed...
            vel = self._calculate_speed(dist, time_elapsed, smoothing_factor=3)
            if vel>self.maxvel:
                self.maxvel=vel

            #The waiting point stuff....
            #This 'fills in' the data for situations where some times are missing from the GPX file
            if time_ is not None:
                if len(waiting_points) > 0:
                    for ((w_total_dist, w_dist, w_alt, w_total_time, w_lat, w_lon, w_hr, w_cadence, w_corEle)) in waiting_points:
                        w_time = (w_dist/dist_elapsed) * time_elapsed
                        w_vel = w_dist/((w_time)/3600.0)
                        w_total_time += w_time
                        logging.info("Time added: %f" % w_time)
                        retorno.append((w_total_dist, w_alt, w_total_time, w_vel, w_lat, w_lon, w_hr, w_cadence, w_corEle))
                    waiting_points = []
                    dist_elapsed = 0
                else:
                    retorno.append((self.total_dist_trkpts,ele, self.total_time,vel,lat,lon,hr,cadence,corEle))
                    dist_elapsed = 0
            else: # time_ is None
                waiting_points.append((self.total_dist_trkpts, dist_elapsed, ele, self.total_time, lat, lon, hr, cadence, corEle))

            #Add to dict of values to trkpoint list
            self.trkpoints.append({ 'id': i,
                                    'lat':lat,
                                    'lon':lon,
                                    'hr':hr,
                                    'cadence':cadence,
                                    'time':time_,
                                    'time_since_previous': time_elapsed,
                                    'time_elapsed': self.total_time_trkpts,
                                    'ele':ele,
                                    'ele_change': rel_alt,
                                    'distance_from_previous': dist,
                                    'elapsed_distance': self.total_dist_trkpts,
                                    'velocity':vel,
                                    'correctedElevation':corEle,

                                })

        #end of for trkpoint in trkpoints loop

        #Calculate averages etc
        self.hr_average = 0
        if len_validhrpoints > 0:
            self.hr_average = total_hr/len_validhrpoints
        # In case there is no other way to calculate distance, we rely on trackpoints (number of trackpoints is configurable!)
        if self.total_dist is None or self.total_dist == 0:
            self.total_dist = self.total_dist_trkpts
        else:
            dist_diff = 1000*(self.total_dist_trkpts - self.total_dist)
            logging.debug("Distance difference between laps and trkpts calculation: %f m" % dist_diff)
        if self.total_time is None or self.total_time == 0:
            self.total_time = self.total_time_trkpts
        else:
            time_diff = self.total_time_trkpts - self.total_time
            logging.debug("Duration difference between laps and trkpts calculation: %d s" % time_diff)
        logging.info("Values - Distance: %.02f km | Duration: %d s | Calories: %s kcal" % (self.total_dist, self.total_time, self.calories))
        logging.debug("<<")
        return retorno

    def _distance_between_points(self, lat1, lon1, lat2, lon2):
        '''
        Function to calculate the distance between two lat, lon points on the earths surface

        History of this function is unknown....
        -- David "no me mates que esto lo escribi hace anhos"
        -- http://faculty.washington.edu/blewis/ocn499/EXER04.htm equation for the distance between 2 points on a spherical earth
        -- 0.01745329252 = number of radians in a degree
        -- 57.29577951 = 1/0.01745329252 or degrees per radian
        requires
            - start lat and lon as floats
            - finish lat and lon as floats

        returns
            - distance between points in kilometers if successful
            - None if any error situation occurs
        '''
        RADIANS_PER_DEGREE = 0.01745329252
        DEGREES_PER_RADIAN = 57.29577951
        #Check for invalid variables
        for var in (lat1, lon1, lat2, lon2):
            if var is None or var == 0 or var == "":   #TODO Need this?? if (float(lat) < -0.000001) or (float(lat) > 0.0000001):
                return None
            if type(var) is not type(float()):
                return None
        #Convert lat and lon from degrees to radians
        last_lat = lat1*RADIANS_PER_DEGREE
        last_lon = lon1*RADIANS_PER_DEGREE
        tmp_lat = lat2*RADIANS_PER_DEGREE
        tmp_lon = lon2*RADIANS_PER_DEGREE
        #Pasamos la distancia de radianes a metros..  creo / We convert the distance from radians to meters
        try:
            dist=math.acos((math.sin(last_lat)*math.sin(tmp_lat))+(math.cos(last_lat)*math.cos(tmp_lat)*math.cos(tmp_lon-last_lon)))*111.302*DEGREES_PER_RADIAN
        except Exception as e:
            logging.debug(str(e))
            dist=None
        return dist

    def _calculate_speed(self, dist_elapsed, time_elapsed, smoothing_factor=3):
        '''Function to calculate moving average for speed'''

        if dist_elapsed is None or dist_elapsed == 0 or time_elapsed is None or time_elapsed == 0:
            velocity = 0
        else:
            velocity = (dist_elapsed/time_elapsed) * 3600 # 3600 to convert km/sec to km/hour
        self.vel_array.append(velocity)
        if len(self.vel_array)>smoothing_factor:
            self.vel_array.pop(0)
        if len(self.vel_array)<smoothing_factor:
            #Got too few numbers to average
            #Pad with duplicates
            for x in range(len(self.vel_array), smoothing_factor):
                self.vel_array.append(velocity)
        vel = 0
        for v in self.vel_array:
            vel+= v
        vel /= smoothing_factor
        return vel

    def getStartTimeFromGPX(self, gpxFile):
        '''03.05.2008 - dgranda
        Retrieves start time from a given gpx file
        args:
            - gpxFile: path to xml file (gpx format)
        returns: tuple (string with start time as UTC timezone - 2008-03-22T12:17:43Z, datetime of time in local timezone)
        '''
        logging.debug(">>")
        date_time = self.tree.find(timeTag) #returns first instance found
        if date_time is None:
            print "Problems when retrieving start time from "+gpxFile+". Please check data integrity"
            return 0
        dateTime = getDateTime(date_time.text)
        zuluDateTime = dateTime[0].strftime("%Y-%m-%dT%H:%M:%SZ")
        localDateTime = dateTime[1]
        logging.debug(gpxFile+" | "+ date_time.text +" | " + zuluDateTime + " | " + str(localDateTime))
        #print localDateTime
        #return date_time.text
        logging.debug("<<")
        return (zuluDateTime, localDateTime)

