# -*- coding: utf-8 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net
#Modified by dgranda

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
import shutil
import logging
import datetime
import warnings

from .gui.windowrecord import WindowRecord
from .gui.dialogselecttrack import DialogSelectTrack
from .lib.date import Date, time2second
from .lib.gpx import Gpx
from pytrainer.core.equipment import EquipmentService, Equipment
from pytrainer.core.sport import Sport
from pytrainer.core.activity import Activity, Lap
from pytrainer.lib.date import DateRange

class Record:
    def __init__(self, sport_service, data_path = None, parent = None):
        logging.debug('>>')
        self._sport_service = sport_service
        self.parent = parent
        self.pytrainer_main = parent
        self._equipment_service = EquipmentService(self.pytrainer_main.ddbb)
        self.data_path = data_path
        logging.debug('setting date...')
        self.date = Date()
        logging.debug('<<')

    def newRecord(self, date, title=None, distance=None, time=None, upositive=None, unegative=None, bpm=None, calories=None, comment=None):
        logging.debug('>>')
        sports = self._sport_service.get_all_sports()
        self.recordwindow = WindowRecord(self._equipment_service, self.data_path, sports, self, self.format_date(date), title, distance, time, upositive, unegative, bpm, calories, comment)
        self.recordwindow.run()
        logging.debug('<<')

    def newMultiRecord(self, activities):
        logging.debug('>>')
        sports = self._sport_service.get_all_sports()
        self.recordwindow = WindowRecord(self._equipment_service, self.data_path, sports, parent=self, windowTitle=_("Modify details before importing"))
        self.recordwindow.populateMultiWindow(activities)
        self.recordwindow.run()
        return self.recordwindow.getActivityData()
        logging.debug('<<')

    def editRecord(self,id_record):
        logging.debug('>>')
        activity = self.pytrainer_main.activitypool.get_activity(id_record)
        sports = self._sport_service.get_all_sports()
        self.recordwindow = WindowRecord(self._equipment_service, self.data_path, sports, self, None, windowTitle=_("Edit Entry"), equipment=activity.equipment)
        self.recordwindow.setValuesFromActivity(activity)
        logging.debug('launching window')
        self.recordwindow.run()
        self.pytrainer_main.refreshMainSportList()
        logging.debug('<<')

    def pace_to_float(self, value):
        '''Take a mm:ss or mm.ss and return float'''
        try:
            value = float(value)
        except:
            if ":" in value: # 'mm:ss' found
                mins, sec = value.split(":")
                value = float(mins + "." + "%02d" %round(int(sec)*5/3))
            elif "," in value:
                value = float(value.replace(',','.'))
            else:
                logging.error("Wrong value provided: %s", value)
                value = None
        return value

    def pace_from_float(self, value, fromDB=False):
        '''Helper to generate mm:ss from float representation mm.ss (or mm,ss?)'''
        if not value:
            return "0:00"
        #Check that value supplied is a float
        try:
            _value = "%0.2f" % float(value)
        except ValueError:
            _value = str(value)
        if fromDB:  # paces in DB are stored in mixed format -> 4:30 as 4.3 (NOT as 4.5 aka 'decimal')
            pace = _value
        else:
            mins, sec_dec = _value.split(".")
            pace = mins + ":" + "%02d" %round(int(sec_dec)*3/5)
        return pace

    def _formatRecordNew(self, list_options, record):
        """20.07.2008 - dgranda
        New records handle date_time_utc field which is transparent when updating, so logic method has been splitted
        args: list with keys and values without valid format
        returns: keys and values matching DB schema"""
        logging.debug('>>')
        if (list_options["rcd_beats"] == ""):
            list_options["rcd_beats"] = 0

        #retrieving sport (adding sport if it doesn't exist yet)
        sport = self._get_sport(list_options["rcd_sport"])
        if not sport:
            sport = Sport(name=list_options["rcd_sport"])
        record.title = list_options["rcd_title"]
        record.beats = self.parseFloatRecord(list_options["rcd_beats"])
        record.pace = self.pace_to_float(list_options["rcd_pace"])
        record.maxbeats = self.parseFloatRecord(list_options["rcd_maxbeats"])
        record.distance = self.parseFloatRecord(list_options["rcd_distance"])
        record.average = self.parseFloatRecord(list_options["rcd_average"])
        record.calories = self.parseFloatRecord(list_options["rcd_calories"])
        record.comments = list_options["rcd_comments"]
        record.date = datetime.datetime.strptime(list_options["rcd_date"],
                                                 "%Y-%m-%d").date()
        record.unegative = self.parseFloatRecord(list_options["rcd_unegative"])
        record.upositive = self.parseFloatRecord(list_options["rcd_upositive"])
        record.maxspeed = self.parseFloatRecord(list_options["rcd_maxvel"])
        record.maxpace = self.pace_to_float(list_options["rcd_maxpace"])
        record.date_time_utc = list_options["date_time_utc"]
        record.duration = time2second(list_options["rcd_time"])
        record.date_time_local = str(list_options["date_time_local"])
        record.sport = sport
        return record

    def insertRecord(self, list_options, laps=None, equipment=None):
        logging.debug('>>')
        #Create entry for activity in records table
        if list_options is None:
            logging.info('No data provided, abort adding entry')
            return None
        logging.debug('list_options: %s', list_options)
        record = self._formatRecordNew(list_options, Activity())
        self.pytrainer_main.ddbb.session.add(record)
        gpxOrig = list_options["rcd_gpxfile"]
        # Load laps from gpx if not provided by the caller
        if laps is None and os.path.isfile(gpxOrig):
            gpx = Gpx(self.data_path, gpxOrig)
            laps = self.lapsFromGPX(gpx)
        #Create entry(s) for activity in laps table
        if laps is not None:
            for lap in laps:
                new_lap = Lap(**lap)
                record.Laps.append(new_lap)
        if equipment:
            record.equipment = self.pytrainer_main.ddbb.session.query(Equipment).filter(Equipment.id.in_(equipment)).all()
        self.pytrainer_main.ddbb.session.commit()
        if os.path.isfile(gpxOrig):
            gpxDest = self.pytrainer_main.profile.gpxdir
            gpxNew = gpxDest+"/%d.gpx" % record.id
            #Leave original file in place...
            #shutil.move(gpxOrig, gpxNew)
            #logging.debug('Moving '+gpxOrig+' to '+gpxNew)
            shutil.copy(gpxOrig, gpxNew)
            logging.debug('Copying %s to %s', gpxOrig, gpxNew)
        logging.debug('<<')
        return record.id

    def insertNewRecord(self, gpxOrig, entry): #TODO consolidate with insertRecord
        """29.03.2008 - dgranda
        Moves GPX file to store destination and updates database
        args: path to source GPX file"""
        logging.debug('--')
        (list_options, gpx_laps) = self.summaryFromGPX(gpxOrig, entry)
        if list_options is None:
            return None
        return self.insertRecord(list_options, laps=gpx_laps)

    def lapsFromGPX(self, gpx):
        logging.debug('>>')
        laps = []
        gpxLaps = gpx.getLaps()
        for lap in gpxLaps:
            lap_number = gpxLaps.index(lap)
            tmp_lap = {}
            tmp_lap['record'] = ""
            tmp_lap['lap_number'] = lap_number
            tmp_lap['elapsed_time'] = lap[0]
            tmp_lap['distance'] = lap[4] or None
            tmp_lap['start_lat'] = lap[5] or None
            tmp_lap['start_lon'] = lap[6] or None
            tmp_lap['end_lat'] = lap[1] or None
            tmp_lap['end_lon'] = lap[2] or None
            tmp_lap['calories'] = lap[3] or None
            tmp_lap['intensity'] = lap[7]
            tmp_lap['avg_hr'] = lap[8] or None
            tmp_lap['max_hr'] = lap[9] or None
            tmp_lap['max_speed'] = lap[10] or None
            tmp_lap['laptrigger'] = lap[11]
            tmp_lap['comments'] = ""
            laps.append(tmp_lap)
        logging.debug('<<')
        return laps

    def hrFromLaps(self, laps):
        logging.debug('>>')
        lap_avg_hr = 0
        lap_max_hr = 0
        total_duration = 0
        ponderate_hr = 0;
        for lap in laps:
            if (lap['max_hr'] is None):
                lap['max_hr'] = 0
            if (lap['avg_hr'] is None):
                lap['avg_hr'] = 0
            if int(lap['max_hr']) > lap_max_hr:
                lap_max_hr = int(lap['max_hr'])
            total_duration = total_duration + float(lap['elapsed_time'])
            ponderate_hr = ponderate_hr + float(lap['elapsed_time'])*int(lap['avg_hr'])
            logging.debug("Lap number: %s | Duration: %s | Average hr: %s | Maximum hr: %s",
                          lap['lap_number'], lap['elapsed_time'], lap['avg_hr'], lap['max_hr'])
        lap_avg_hr = int(round(ponderate_hr/total_duration)) # ceil?, floor?, round?
        logging.debug('<<')
        return lap_avg_hr, lap_max_hr

    def summaryFromGPX(self, gpxOrig, entry):
        """29.03.2008 - dgranda
        Retrieves info which will be stored in DB from GPX file
        args: path to source GPX file
        returns: list with fields and values, list of laps
        """
        logging.debug('>>')
        gpx = Gpx(self.data_path,gpxOrig)
        distance, time, maxspeed, maxheartrate = gpx.getMaxValues()
        #if time == 0: #invalid record
        #       print "Invalid record"
        #       return (None, None)
        upositive,unegative = gpx.getUnevenness()
        if time > 0:
            speed = distance*3600/time
            time_hhmmss = [time//3600,(time/60)%60,time%60]
        else:
            speed = 0
            time_hhmmss = [0,0,0]
        summaryRecord = {}
        summaryRecord['rcd_gpxfile'] = gpxOrig
        summaryRecord['rcd_sport'] = entry[0]
        summaryRecord['rcd_date'] = gpx.getDate()
        summaryRecord['rcd_calories'] = gpx.getCalories()
        summaryRecord['rcd_comments'] = ''
        summaryRecord['rcd_title'] = ''
        summaryRecord['rcd_time'] = time_hhmmss #ToDo: makes no sense to work with arrays
        summaryRecord['rcd_distance'] = "%0.2f" %distance
        if speed == 0:
            summaryRecord['rcd_pace'] = "0"
        else:
            summaryRecord['rcd_pace'] = "%d.%02d" %((3600/speed)/60,(3600/speed)%60)
        if maxspeed == 0:
            summaryRecord['rcd_maxpace'] = "0"
        else:
            summaryRecord['rcd_maxpace'] = "%d.%02d" %((3600/maxspeed)/60,(3600/maxspeed)%60)
        summaryRecord['rcd_average'] = speed
        summaryRecord['rcd_maxvel'] = maxspeed
        summaryRecord['rcd_beats'] = gpx.getHeartRateAverage()
        summaryRecord['rcd_maxbeats'] = maxheartrate
        summaryRecord['rcd_upositive'] = upositive
        summaryRecord['rcd_unegative'] = unegative
        if entry[1]=="": # coming from new track dialog (file opening)                                                                                          #TODO This if-else needs checking
            summaryRecord['date_time_utc'], summaryRecord['date_time_local'] = gpx.getStartTimeFromGPX(gpxOrig)             #
        else: # coming from GPS device                                                                                                                                                          #
            summaryRecord['date_time_utc'] = entry[1]                                                                                                                               #
            summaryRecord['date_time_local'] = entry[1]                                                                                                                             #
            #TODO fix record summaryRecord local and utc time...
        logging.debug('summary: %s', summaryRecord)
        laps = self.lapsFromGPX(gpx)
        # Heartrate data can't be retrieved if no trackpoints present, calculating from lap info
        lap_avg_hr, lap_max_hr = self.hrFromLaps(laps)
        logging.debug("HR data from laps. Average: %s | Maximum hr: %s", lap_avg_hr, lap_max_hr)
        if int(summaryRecord['rcd_beats']) > 0:
            logging.debug("Average heartbeat - Summary: %s | Laps: %s", summaryRecord['rcd_beats'],
                          lap_avg_hr)
        else:
            logging.debug("No average heartbeat found, setting value (%s) from laps", lap_avg_hr)
            summaryRecord['rcd_beats'] = lap_avg_hr
        if int(summaryRecord['rcd_maxbeats']) > 0:
            logging.debug("Max heartbeat - Summary: %s | Laps: %s", summaryRecord['rcd_maxbeats'],
                          lap_max_hr)
        else:
            logging.debug("No max heartbeat found, setting value (%s) from laps", lap_max_hr)
            summaryRecord['rcd_maxbeats'] = lap_max_hr
        logging.debug('<<')
        return summaryRecord, laps

    def updateRecord(self, list_options, id_record, equipment=None): # ToDo: update only fields that can change if GPX file is present
        logging.debug('>>')
        logging.debug('list_options: %s', list_options)
        # No need to remove from the pool, sqlalchemy keeps things in sync
        record = self.pytrainer_main.activitypool.get_activity(id_record)
        gpxfile = self.pytrainer_main.profile.gpxdir+"/%d.gpx"%int(record.id)
        gpxOrig = list_options["rcd_gpxfile"]
        if os.path.isfile(gpxOrig):
            if gpxfile != gpxOrig:
                shutil.copy2(gpxOrig, gpxfile)
        else:
            if (list_options["rcd_gpxfile"]==""):
                logging.debug('Activity not based in GPX file') # ein?
        logging.debug('Updating bbdd')
        self._formatRecordNew(list_options, record)
        if equipment:
            record.equipment = self.pytrainer_main.ddbb.session.query(Equipment).filter(Equipment.id.in_(equipment)).all()
        self.pytrainer_main.ddbb.session.commit()
        self.pytrainer_main.refreshListView()
        logging.debug('<<')

    def parseFloatRecord(self,string):
        logging.debug('--')
        if string != "":
            try:
                return float(string.replace(",",","))
            except:
                return float(string)
        else:
            return 0

    def format_date(self, date):
        return date.strftime("%Y-%m-%d")

    def _get_sport(self, sport_name):
        return self._sport_service.get_sport_by_name(sport_name)

    def getSportMet(self,sport_name):
        """Deprecated: use sport.met"""
        warnings.warn('Deprecated call to getSportMet', DeprecationWarning, stacklevel=2)
        return self._get_sport(sport_name).met

    def getSportWeight(self,sport_name):
        """Deprecated: use sport.weight"""
        warnings.warn('Deprecated call to getSportWeight', DeprecationWarning, stacklevel=2)
        return self._get_sport(sport_name).weight

    def getLastRecordDateString(self, sport_id = None):
        """
        Retrieve date (string format) of last record stored in DB. It may select per sport
        """
        logging.debug("--")
        if sport_id is not None:
            return str(self.pytrainer_main.ddbb.session.query(Activity).
                       filter(Activity.sport_id == sport_id).order_by(Activity.date.desc()).
                       limit(1).one().date)
        else:
            return str(self.pytrainer_main.ddbb.session.query(Activity).order_by(Activity.date.desc()).
                       limit(1).one().date)

    def getAllrecord(self):
        """
        Retrieve all record data (no lap nor equipment) stored in database. Initially intended for csv export
        arguments:
        returns: list of data sorted by date desc"""
        logging.debug('--')
        return self.pytrainer_main.ddbb.select("records,sports", "date_time_local,title,sports.name,distance,duration,average,maxspeed,pace,maxpace,beats,maxbeats,calories,upositive,unegative,comments",
    "sports.id_sports = records.sport","order by date_time_local asc")

    def getRecordListByCondition(self, condition):
        logging.debug('>>')
        if condition is None:
            return self.pytrainer_main.ddbb.session.query(Activity).order_by(Activity.date.desc())
        else:
            return self.pytrainer_main.ddbb.session.query(Activity).filter(condition).order_by(Activity.date.desc())

    def getRecordDayList(self, date, sport=None):
        logging.debug('>>')
        logging.debug('Retrieving data for %s', date)
        date_range = DateRange.for_month_containing(date)
        for activity in self.pytrainer_main.activitypool.get_activities_period(date_range, sport=sport):
            yield activity.date.day

    def actualize_fromgpx(self,gpxfile): #TODO remove? - should never have multiple tracks per GPX file
        logging.debug('>>')
        logging.debug('loading file: %s', gpxfile)
        gpx = Gpx(self.data_path,gpxfile)
        tracks = gpx.getTrackRoutes()

        if len(tracks) == 1:
            logging.debug('Just 1 track')
            self._actualize_fromgpx(gpx)
        elif len(tracks) > 1:
            logging.debug('Found %s tracks', len(tracks))
            self._select_trkfromgpx(gpxfile,tracks)
        else:
            msg = _("pytrainer can't import data from your gpx file")
            from .gui.warning import Warning
            warning = Warning(self.data_path)
            warning.set_text(msg)
            warning.run()
        logging.debug('<<')

    def _actualize_fromgpx(self, gpx):
        logging.debug('>>')
        distance, time, maxspeed, maxheartrate = gpx.getMaxValues()
        upositive,unegative = gpx.getUnevenness()
        heartrate = gpx.getHeartRateAverage()
        date = gpx.getDate()
        calories = gpx.getCalories()
        start_time = gpx.getStart_time()

        self.recordwindow.rcd_date.set_text(date)
        self.recordwindow.rcd_starttime.set_text(start_time)
        self.recordwindow.rcd_upositive.set_text(str(upositive))
        self.recordwindow.rcd_unegative.set_text(str(unegative))
        self.recordwindow.rcd_beats.set_text(str(heartrate))
        self.recordwindow.rcd_calories.set_text(str(calories))
        self.recordwindow.set_distance(distance)
        self.recordwindow.set_maxspeed(maxspeed)
        self.recordwindow.set_maxhr(maxheartrate)
        self.recordwindow.set_recordtime(time/60.0/60.0)
        self.recordwindow.on_calcavs_clicked(None)
        self.recordwindow.on_calccalories_clicked(None)
        self.recordwindow.rcd_maxpace.set_text("%d.%02d" %((3600/maxspeed)/60,(3600/maxspeed)%60))
        logging.debug('<<')

    def __actualize_fromgpx(self, gpxfile, name=None):
        logging.debug('>>')
        gpx = Gpx(self.data_path,gpxfile,name)
        self._actualize_fromgpx(gpx)
        logging.debug('<<')

    def _select_trkfromgpx(self,gpxfile,tracks):  #TODO remove? - should never have multiple tracks per GPX file
        logging.debug('>>')
        logging.debug('Track dialog %s|%s', self.data_path, gpxfile)
        selectrckdialog = DialogSelectTrack(self.data_path, tracks,self.__actualize_fromgpx, gpxfile)
        logging.debug('Launching window...')
        selectrckdialog.run()
        logging.debug('<<')

    def importFromGPX(self, gpxFile, sport):
        """
        Add a record from a valid pytrainer type GPX file
        """
        logging.debug('>>')
        entry_id = None
        if not os.path.isfile(gpxFile):
            logging.error("Invalid file: %s", gpxFile)
        else:
            logging.info('Retrieving data from %s', gpxFile)
            if not sport:
                sport = "import"
            entry = [sport,""]
            entry_id = self.insertNewRecord(gpxFile, entry)
            if entry_id is None:
                logging.error("Entry not created for file %s", gpxFile)
            else:
                logging.info("Entry %d has been added", entry_id)
        logging.debug('<<')
        return entry_id
