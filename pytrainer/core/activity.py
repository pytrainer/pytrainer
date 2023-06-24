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

import logging
import warnings
import os, os.path
import dateutil.parser
from dateutil.tz import tzlocal

from pytrainer.lib.date import second2time
from pytrainer.lib.gpx import Gpx
from pytrainer.environment import Environment
from pytrainer.lib import uc
from pytrainer.profile import Profile
from pytrainer.lib.ddbb import DeclarativeBase, ForcedInteger, record_to_equipment
from sqlalchemy import Column, Integer, Float, UnicodeText, Date, ForeignKey, String, Unicode, and_
from sqlalchemy.orm import relationship, backref, reconstructor, deferred, joinedload
from sqlalchemy.exc import InvalidRequestError

class Lap(DeclarativeBase):
    __tablename__ = 'laps'
    avg_hr = Column(ForcedInteger)
    calories = Column(ForcedInteger)
    comments = Column(UnicodeText)
    distance = Column(Float)
    elapsed_time = Column(String(length=20))
    end_lat = Column(Float)
    end_lon = Column(Float)
    id_lap = Column(Integer, primary_key=True)
    intensity = Column(String(length=7))
    lap_number = Column(ForcedInteger)
    laptrigger = Column(String(length=9))
    max_hr = Column(ForcedInteger)
    max_speed = Column(Float)
    record = Column(Integer, ForeignKey('records.id_record'), index=True, nullable=False)
    start_lat = Column(Float)
    start_lon = Column(Float)

    @property
    def duration(self):
        return float(self.elapsed_time)

class ActivityServiceException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class ActivityService(object):
    '''
    Class maintains a pool of activities
            size is set at initialisation
    '''
    def __init__(self, pytrainer_main=None, size=1):
        logging.debug(">>")
        #It is an error to try to initialise with no reference to pytrainer_main
        if pytrainer_main is None:
            logging.critical("Error - must initialise with a reference to the main pytrainer class")
            return
        self.pytrainer_main = pytrainer_main
        self.max_size = size
        self.pool = {}
        self.pool_queue = []
        logging.debug("Initialising ActivityPool to size: %d", size)
        logging.debug("<<")

    def clear_pool(self):
        logging.debug(">>")
        logging.debug("Clearing ActivityPool")
        self.pool = {}
        self.pool_queue = []
        logging.debug("<<")

    def remove_activity_from_cache(self, id):
        sid = str(id)
        if sid in list(self.pool.keys()):
            logging.debug("Found activity in pool")
            self.pool_queue.remove(sid)
            del self.pool[sid]

    def get_activity(self, id):
        if id is None:
            warnings.warn("Deprecated call to get_activity with None id", DeprecationWarning, stacklevel=2)
            return Activity()
        sid = str(id)
        if sid in list(self.pool.keys()):
            logging.debug("Found activity in pool")
            #Have accessed this activity, place at end of queue
            self.pool_queue.remove(sid)
            self.pool_queue.append(sid)
        else:
            logging.debug("Activity NOT found in pool")
            self.pool[sid] = self.pytrainer_main.ddbb.session.query(Activity).options(
                joinedload(Activity.sport),
                joinedload(Activity.equipment),
                joinedload(Activity.Laps)
            ).filter(Activity.id == id).one()
            self.pool_queue.append(sid)
        if len(self.pool_queue) > self.max_size:
            sid_to_remove = self.pool_queue.pop(0)
            logging.debug("Removing activity: %s", sid_to_remove)
            del self.pool[sid_to_remove]
        logging.debug("ActivityPool queue length: %d", len(self.pool_queue))
        logging.debug("ActivityPool queue: %s", self.pool_queue)
        return self.pool[sid]

    def remove_activity_from_db(self, activity):
        """Delete a stored Activity."""

        if not activity.id:
            raise ActivityServiceException("Cannot remove activity which has not been stored: '{0}'.".format(activity.name))
        try:
            self.remove_activity_from_cache(activity.id)
            self.pytrainer_main.ddbb.session.delete(activity)
            self.pytrainer_main.ddbb.session.commit()
            if activity.gpx_file and os.path.isfile(activity.gpx_file):
                os.remove(activity.gpx_file)
        except InvalidRequestError:
             raise ActivityServiceException("Activity id %s not found" % activity.id)
        logging.debug("Deleted activity: %s", activity.title)

    def get_activities_for_day(self, date, sport=None):
        """Iterates the activities for a specific date, optionally restricted by Sport)"""
        if not sport:
            activities = self.pytrainer_main.ddbb.session.query(Activity).filter(Activity.date == date).options(joinedload(Activity.Laps))
        else:
            activities = self.pytrainer_main.ddbb.session.query(Activity).filter(and_(Activity.date == date, Activity.sport == sport)).options(joinedload(Activity.Laps))
        for activity in activities:
            sid = str(activity.id)
            if sid in self.pool:
                yield self.pool[sid]
            else:
                self.pool[sid] = activity
                self.pool_queue.append(sid)
                yield activity

    def get_activities_period(self, date_range, sport=None):
        """Iterate over activities for a specific time period, optionally restricted by Sport.
Does not add them to the cache."""
        if not sport:
            return self.pytrainer_main.ddbb.session.query(Activity).filter(Activity.date.between(date_range.start_date, date_range.end_date))
        else:
            return self.pytrainer_main.ddbb.session.query(Activity).filter(and_(Activity.date.between(date_range.start_date, date_range.end_date), Activity.sport == sport))

    def get_all_activities(self):
        """Iterates over all activities ordered by date"""
        return self.pytrainer_main.ddbb.session.query(Activity).order_by('date')

class Activity(DeclarativeBase):
    '''
    Class that knows everything about a particular activity

    All values are stored in the class (and DB) in metric and are converted as needed

    tracks                  - (list) tracklist from gpx
    tracklist               - (list of dict) trackpoint data from gpx
    laps                    - (list of dict) lap list
    us_system               - (bool) True: imperial measurement False: metric measurement
    distance_data   - (dict of graphdata classes) contains the graph data with x axis distance
    time_data               - (dict of graphdata classes) contains the graph data with x axis time
    gpx_file                - (string) gpx file name
    gpx                             - (Gpx class) actual gpx instance
    sport_name              - (string) sport name
    sport_id                - (string) id for sport in sports table
    title                   - (string) title of activity
    date                    - (string) date of activity
    time                    - (int) activity duration in seconds
    time_tuple              - (tuple) activity duration as hours, min, secs tuple
    beats                   - (int) average heartrate for activity
    maxbeats                - (int) maximum heartrate for activity
    comments                - (string) activity comments
    calories                - (int) calories of activity
    id                      - (int) id for activity in records table
    date_time_local - (string) date and time of activity in local timezone
    date_time_utc   - (string) date and time of activity in UTC timezone
    date_time               - (datetime) date and time of activity in local timezone
    starttime               - (string)
    distance                - (float) activity distance
    average                 - (float) average speed of activity
    upositive               - (float) height climbed during activity
    unegative               - (float) height decended during activity
    maxspeed                - (float) maximum speed obtained during activity
    maxpace                 - (float) maxium pace obtained during activity
    pace                    - (float) average pace for activity
    has_data                - (bool) true if instance has data populated
    x_axis                  - (string) distance or time, determines what will be graphed on x axis
    x_limits                - (tuple of float) start, end limits of x axis (as determined by matplotlib)
    y1_limits               - (tuple of float) start, end limits of y1 axis (as determined by matplotlib)
    y2_limits               - (tuple of float) start, end limits of y2 axis (as determined by matplotlib)
    x_limits_u              - (tuple of float) start, end limits of x axis (as requested by user)
    y1_limits_u             - (tuple of float) start, end limits of y1 axis (as requested by user)
    y2_limits_u             - (tuple of float) start, end limits of y2 axis (as requested by user)
    show_laps               - (bool) display laps on graphs
    lap_distance    - (graphdata)
    lap_time                - (graphdata)
    pace_limit              - (int) maximum pace that is valid for this activity
    '''
    __tablename__ = 'records'
    average = Column(Float)
    beats = Column(Float)
    calories = Column(ForcedInteger)
    comments = Column(UnicodeText)
    date = Column(Date)
    date_time_local = Column(String(length=40))
    date_time_utc = Column(String(length=40))
    distance = Column(Float)
    duration = Column(ForcedInteger)
    gpslog = deferred(Column(String(length=200)))
    id = Column("id_record", Integer, primary_key=True)
    maxbeats = Column(Float)
    maxpace = Column(Float)
    maxspeed = Column(Float)
    pace = Column(Float)
    sport_id = Column("sport", Integer, ForeignKey('sports.id_sports'),
                          index=True, nullable=False)
    title = Column(Unicode(length=200))
    unegative = Column(Float)
    upositive = Column(Float)

    #relation definitions
    sport = relationship("Sport", backref=backref("activities", order_by=date,
                                                  cascade='all, delete-orphan'))
    equipment = relationship("Equipment", secondary=record_to_equipment,
                             backref=backref("activities", order_by=date))
    Laps = relationship('Lap', backref=backref('activity'),
                        order_by='Lap.lap_number',
                        cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        self._initialize()
        super(Activity, self).__init__(**kwargs)

    @reconstructor
    def _initialize(self):
        logging.debug(">>")
        self.environment = Environment()
        self.uc = uc.UC()
        self.profile = Profile()
        self.has_data = True
        self._distance_data = {}
        self._time_data = {}
        self._lap_time = None
        self._lap_distance = None
        self.time_pause = 0
        self.pace_limit = None
        self._gpx = None
        self.x_axis = "distance"
        self.x_limits = (None, None)
        self.y1_limits = (None, None)
        self.y2_limits = (None, None)
        self.x_limits_u = (None, None)
        self.y1_limits_u = (None, None)
        self.y2_limits_u = (None, None)
        self.y1_grid = False
        self.y2_grid = False
        self.x_grid = False
        self.show_laps = False
        logging.debug("<<")

    @property
    def gpx_file(self):
        if self.id:
            filename = "%s/%s.gpx" % (self.environment.gpx_dir, self.id)
            #It is OK to not have a GPX file for an activity - this just limits us to information in the DB
            if os.path.isfile(filename):
                return filename
        logging.debug("No GPX file found for record id: %s", self.id)
        return None

    @property
    def tracks(self):
        if self.gpx:
            return self.gpx.getTrackList()
        else:
            return None

    @property
    def tracklist(self):
        if self.gpx:
            return self.gpx.trkpoints
        else:
            return None

    @property
    def distance_data(self):
        if not self._distance_data:
            self._init_graph_data()
        return self._distance_data

    @property
    def time_data(self):
        if not self._time_data:
            self._init_graph_data()
        return self._time_data

    @property
    def lap_time(self):
        if not self._lap_time:
            self._generate_per_lap_graphs()
        return self._lap_time

    @property
    def lap_distance(self):
        if not self._lap_distance:
            self._generate_per_lap_graphs()
        return self._lap_distance

    @property
    def time_tuple(self):
        return second2time(self.duration)

    @property
    def date_time(self):
        if self.date_time_local: #Have a local time stored in DB
            return dateutil.parser.parse(self.date_time_local)
        else: #No local time in DB
            #datetime with localtime offset (using value from OS)
            return dateutil.parser.parse(self.date_time_utc).astimezone(tzlocal())

    @property
    def starttime(self):
        return self.date_time.strftime("%X")

    @property
    def laps(self):
        warnings.warn("Deprecated property Activity.laps called", DeprecationWarning, stacklevel=2)
        ret = []
        for lap in self.Laps:
            d = dict(lap.__dict__)
            d.pop('_sa_instance_state', None)
            ret.append(d)
        return ret

    def __str__(self):
        return '''
tracks (%s)
        tracklist (%s)
        laps (%s)
        us_system (%s)
        distance_data (%s)
        time_data (%s)
        gpx_file (%s)
        gpx (%s)
        sport_name (%s)
        sport_id (%s)
        title (%s)
        date (%s)
        time (%s)
        time_tuple (%s)
        beats (%s)
        maxbeats (%s)
        comments (%s)
        calories (%s)
        id (%s)
        date_time_local (%s)
        date_time_utc (%s)
        date_time (%s)
        starttime (%s)
        distance (%s)
        average (%s)
        upositive (%s)
        unegative (%s)
        maxspeed (%s)
        maxpace (%s)
        pace (%s)
        has_data (%s)
        x_axis (%s)
        x_limits (%s)
        y1_limits (%s)
        y2_limits (%s)
        x_limits_u (%s)
        y1_limits_u (%s)
        y2_limits_u (%s)
        show_laps (%s)
        lap_distance (%s)
        lap_time (%s)
        pace_limit (%s)
''' % ('self.tracks', self.tracklist, self.laps, self.uc.us,
                self.distance_data, self.time_data,
                self.gpx_file, self.gpx, self.sport_name,
                self.sport_id, self.title, self.date, self.duration, self.time_tuple, self.beats,
                self.maxbeats, self.comments, self.calories, self.id, self.date_time_local,
                self.date_time_utc, self.date_time, self.starttime, self.distance, self.average,
                self.upositive, self.unegative, self.maxspeed, self.maxpace, self.pace, self.has_data,
                self.x_axis, self.x_limits, self.y1_limits, self.y2_limits, self.x_limits_u, self.y1_limits_u,
                self.y2_limits_u, self.show_laps, self.lap_distance, self.lap_time, self.pace_limit)

    @property
    def gpx(self):
        '''
        Get activity information from the GPX file
        '''
        logging.debug(">>")
        if self._gpx:
            logging.debug("Return pre-created GPX")
            return self._gpx
        elif self.gpx_file:
            logging.debug("Parse GPX")
            #Parse GPX file
            #print "Activity initing GPX.. ",
            self._gpx = Gpx(filename=self.gpx_file) #TODO change GPX code to do less....
            logging.info("GPX Distance: %s | distance (trkpts): %s | duration: %s | duration (trkpts): %s",
                         self.gpx.total_dist, self.gpx.total_dist_trkpts, self.gpx.total_time,
                         self.gpx.total_time_trkpts)
            time_diff = self.gpx.total_time_trkpts - self.gpx.total_time
            acceptable_lapse = 4 # number of seconds that duration calculated using lap and trkpts data can differ
            if time_diff > acceptable_lapse:
                self.time_pause = time_diff
                logging.debug("Identified non active time: %s s", self.time_pause)
            return self._gpx
        else:
            logging.debug("No GPX file found")
            return None
        logging.debug("<<")

    @property
    def time(self):
        warnings.warn("Deprecated property Activity.time called", DeprecationWarning, stacklevel=2)
        return self.duration

    @property
    def sport_name(self):
        warnings.warn("Deprecated property Activity.sport_name called", DeprecationWarning, stacklevel=2)
        return self.sport.name

    def _generate_per_lap_graphs(self):
        from pytrainer.lib.graphdata import GraphData
        '''Build lap based graphs...'''
        logging.debug(">>")
        if self.laps is None:
            logging.debug("No laps to generate graphs from")
            logging.debug("<<")
            return
        #Lap columns
        self._lap_distance = GraphData()
        self._lap_distance.set_color('#CCFF00', '#CCFF00')
        self._lap_distance.graphType = "vspan"
        self._lap_time = GraphData()
        self._lap_time.set_color('#CCFF00', '#CCFF00')
        self._lap_time.graphType = "vspan"
        #Pace
        title = _("Pace by Lap")
        xlabel = "%s (%s)" % (_('Distance'), self.uc.unit_distance)
        ylabel = "%s (%s)" % (_('Pace'), self.uc.unit_pace)
        self.distance_data['pace_lap'] = GraphData(title=title, xlabel=xlabel, ylabel=ylabel)
        self.distance_data['pace_lap'].set_color('#99CCFF', '#99CCFF')
        self.distance_data['pace_lap'].graphType = "bar"
        xlabel=_("Time (seconds)")
        self.time_data['pace_lap'] = GraphData(title=title, xlabel=xlabel, ylabel=ylabel)
        self.time_data['pace_lap'].set_color('#99CCFF', '#99CCFF')
        self.time_data['pace_lap'].graphType = "bar"
        #Speed
        title = _("Speed by Lap")
        xlabel = "%s (%s)" % (_('Distance'), self.uc.unit_distance)
        ylabel = "%s (%s)" % (_('Speed'), self.uc.unit_speed)
        self.distance_data['speed_lap'] = GraphData(title=title, xlabel=xlabel, ylabel=ylabel)
        self.distance_data['speed_lap'].set_color('#336633', '#336633')
        self.distance_data['speed_lap'].graphType = "bar"
        xlabel = _("Time (seconds)")
        self.time_data['speed_lap'] = GraphData(title=title, xlabel=xlabel, ylabel=ylabel)
        self.time_data['speed_lap'].set_color('#336633', '#336633')
        self.time_data['speed_lap'].graphType = "bar"
        for lap in self.laps:
            time = float(lap['elapsed_time']) # time in sql is a unicode string
            dist = lap['distance']/1000 #distance in km
            try:
                pace = time/(60*dist) #min/km
            except ZeroDivisionError:
                pace = 0.0
            try:
                avg_speed = dist/(time/3600) # km/hr
            except:
                avg_speed = 0.0
            if self.pace_limit is not None and pace > self.pace_limit:
                logging.debug("Pace (%s) exceeds limit (%s). Setting to 0", pace, self.pace_limit)
                pace = 0.0
            logging.debug("Time: %f, Dist: %f, Pace: %f, Speed: %f", time, dist, pace, avg_speed)
            self._lap_time.addBars(x=time, y=10)
            self._lap_distance.addBars(x=self.uc.distance(dist), y=10)
            self.distance_data['pace_lap'].addBars(x=self.uc.distance(dist), y=self.uc.distance(pace))
            self.time_data['pace_lap'].addBars(x=time, y=self.uc.speed(pace))
            self.distance_data['speed_lap'].addBars(x=self.uc.distance(dist), y=self.uc.speed(avg_speed))
            self.time_data['speed_lap'].addBars(x=time, y=self.uc.speed(avg_speed))
        logging.debug("<<")

    def _init_graph_data(self):
        from pytrainer.lib.graphdata import GraphData
        logging.debug(">>")
        if self.tracklist is None:
            logging.debug("No tracklist in activity")
            logging.debug("<<")
            return
        #Profile
        title = _("Elevation")
        xlabel = "%s (%s)" % (_('Distance'), self.uc.unit_distance)
        ylabel = "%s (%s)" % (_('Elevation'), self.uc.unit_height)
        self._distance_data['elevation'] = GraphData(title=title, xlabel=xlabel, ylabel=ylabel)
        self._distance_data['elevation'].set_color('#ff0000', '#ff0000')
        self._distance_data['elevation'].show_on_y1 = True #Make graph show elevation by default
        xlabel = _("Time (seconds)")
        self._time_data['elevation'] = GraphData(title=title,xlabel=xlabel, ylabel=ylabel)
        self._time_data['elevation'].set_color('#ff0000', '#ff0000')
        self._time_data['elevation'].show_on_y1 = True #Make graph show elevation by default
        #Corrected Elevation...
        title = _("Corrected Elevation")
        xlabel = "%s (%s)" % (_('Distance'), self.uc.unit_distance)
        ylabel = "%s (%s)" % (_('Corrected Elevation'), self.uc.unit_height)
        self._distance_data['cor_elevation'] = GraphData(title=title, xlabel=xlabel, ylabel=ylabel)
        self._distance_data['cor_elevation'].set_color('#993333', '#993333')
        xlabel=_("Time (seconds)")
        self._time_data['cor_elevation'] = GraphData(title=title,xlabel=xlabel, ylabel=ylabel)
        self._time_data['cor_elevation'].set_color('#993333', '#993333')
        #Speed
        title = _("Speed")
        xlabel = "%s (%s)" % (_('Distance'), self.uc.unit_distance)
        ylabel = "%s (%s)" % (_('Speed'), self.uc.unit_speed)
        self._distance_data['speed'] = GraphData(title=title, xlabel=xlabel, ylabel=ylabel)
        self._distance_data['speed'].set_color('#000000', '#000000')
        xlabel = _("Time (seconds)")
        self._time_data['speed'] = GraphData(title=title,xlabel=xlabel, ylabel=ylabel)
        self._time_data['speed'].set_color('#000000', '#000000')
        #Pace
        title = _("Pace")
        xlabel = "%s (%s)" % (_('Distance'), self.uc.unit_distance)
        ylabel = "%s (%s)" % (_('Pace'), self.uc.unit_pace)
        self._distance_data['pace'] = GraphData(title=title, xlabel=xlabel, ylabel=ylabel)
        self._distance_data['pace'].set_color('#0000ff', '#0000ff')
        xlabel = _("Time (seconds)")
        self._time_data['pace'] = GraphData(title=title,xlabel=xlabel, ylabel=ylabel)
        self._time_data['pace'].set_color('#0000ff', '#0000ff')
        #Heartrate
        title = _("Heart Rate")
        xlabel = "%s (%s)" % (_('Distance'), self.uc.unit_distance)
        ylabel = "%s (%s)" % (_('Heart Rate'), _('bpm'))
        self._distance_data['hr'] = GraphData(title=title, xlabel=xlabel, ylabel=ylabel)
        self._distance_data['hr'].set_color('#00ff00', '#00ff00')
        xlabel = _("Time (seconds)")
        self._time_data['hr'] = GraphData(title=title,xlabel=xlabel, ylabel=ylabel)
        self._time_data['hr'].set_color('#00ff00', '#00ff00')
        #Heartrate as %
        maxhr = self.profile.getMaxHR()
        title = _("Heart Rate (% of max)")
        xlabel = "%s (%s)" % (_('Distance'), self.uc.unit_distance)
        ylabel = "%s (%s)" % (_('Heart Rate'), _('%'))
        self._distance_data['hr_p'] = GraphData(title=title, xlabel=xlabel, ylabel=ylabel)
        self._distance_data['hr_p'].set_color('#00ff00', '#00ff00')
        xlabel = _("Time (seconds)")
        self._time_data['hr_p'] = GraphData(title=title, xlabel=xlabel, ylabel=ylabel)
        self._time_data['hr_p'].set_color('#00ff00', '#00ff00')
        #Cadence
        title = _("Cadence")
        xlabel = "%s (%s)" % (_('Distance'), self.uc.unit_distance)
        ylabel = "%s (%s)" % (_('Cadence'), _('rpm'))
        self._distance_data['cadence'] = GraphData(title=title, xlabel=xlabel, ylabel=ylabel)
        self._distance_data['cadence'].set_color('#cc00ff', '#cc00ff')
        xlabel = _("Time (seconds)")
        self._time_data['cadence'] = GraphData(title=title, xlabel=xlabel, ylabel=ylabel)
        self._time_data['cadence'].set_color('#cc00ff', '#cc00ff')
        for track in self.tracklist:
            try:
                pace = 60/track['velocity']
                if self.pace_limit is not None and pace > self.pace_limit:
                    logging.debug("Pace (%s) exceeds limit (%s). Setting to 0", pace, self.pace_limit)
                    pace = 0  #TODO this should be None when we move to newgraph...
            except Exception as e:
                #print type(e), e
                pace = 0
            try:
                hr_p = float(track['hr'])/maxhr*100
            except:
                hr_p = 0
            self._distance_data['elevation'].addPoints(x=self.uc.distance(track['elapsed_distance']),
                                                       y=self.uc.height(track['ele']))
            self._distance_data['cor_elevation'].addPoints(x=self.uc.distance(track['elapsed_distance']),
                                                           y=self.uc.height(track['correctedElevation']))
            self._distance_data['speed'].addPoints(x=self.uc.distance(track['elapsed_distance']),
                                                   y=self.uc.speed(track['velocity']))
            self._distance_data['pace'].addPoints(x=self.uc.distance(track['elapsed_distance']),
                                                  y=self.uc.distance(pace))
            self._distance_data['hr'].addPoints(x=self.uc.distance(track['elapsed_distance']),
                                                y=track['hr'])
            self._distance_data['hr_p'].addPoints(x=self.uc.distance(track['elapsed_distance']),
                                                  y=hr_p)
            self._distance_data['cadence'].addPoints(x=self.uc.distance(track['elapsed_distance']),
                                                     y=track['cadence'])
            self._time_data['elevation'].addPoints(x=track['time_elapsed'],
                                                   y=self.uc.height(track['ele']))
            self._time_data['cor_elevation'].addPoints(x=track['time_elapsed'],
                                                       y=self.uc.height(track['correctedElevation']))
            self._time_data['speed'].addPoints(x=track['time_elapsed'],
                                               y=self.uc.speed(track['velocity']))
            self._time_data['pace'].addPoints(x=track['time_elapsed'],
                                              y=self.uc.distance(pace))
            self._time_data['hr'].addPoints(x=track['time_elapsed'], y=track['hr'])
            self._time_data['hr_p'].addPoints(x=track['time_elapsed'], y=hr_p)
            self._time_data['cadence'].addPoints(x=track['time_elapsed'], y=track['cadence'])
        #Remove data with no values
        for item in list(self._distance_data.keys()):
            if len(self._distance_data[item]) == 0:
                logging.debug("No values for %s. Removing....", item)
                del self._distance_data[item]
        for item in list(self._time_data.keys()):
            if len(self._time_data[item]) == 0:
                logging.debug("No values for %s. Removing....", item)
                del self._time_data[item]
        logging.debug("<<")
        #Add Heartrate zones graphs
        if 'hr' in self._distance_data:
            zones = self.profile.getZones()
            title = _("Heart Rate zone")
            xlabel = "%s (%s)" % (_('Distance'), self.uc.unit_distance)
            ylabel = "%s (%s)" % (_('Heart Rate'), _('bpm'))
            self._distance_data['hr_z'] = GraphData(title=title, xlabel=xlabel, ylabel=ylabel)
            self._distance_data['hr_z'].graphType = "hspan"
            self._distance_data['hr_z'].set_color(None, None)
            xlabel = _("Time (seconds)")
            self._time_data['hr_z'] = GraphData(title=title,xlabel=xlabel, ylabel=ylabel)
            self._time_data['hr_z'].set_color(None, None)
            for zone in zones:
                self._distance_data['hr_z'].addPoints(x=zone[0], y=zone[1], label=zone[3], color=zone[2])
                self._time_data['hr_z'].addPoints(x=zone[0], y=zone[1], label=zone[3], color=zone[2])

    def _float(self, value):
        try:
            result = float(value)
        except:
            result = 0.0
        return result

    def _int(self, value):
        try:
            result = int(value)
        except:
            result = 0
        return result

    def get_value_f(self, param, format=None):
        ''' Function to return a value formated as a string
                - takes into account US/metric
                - also appends units if required
        '''
        value = self.get_value(param)
        if not value:
            #Return blank string if value is None or 0
            return ""
        if format is not None:
            result = format % value
        else:
            result = str(value)
        return result

    def get_value(self, param):
        ''' Function to get the value of various params in this activity instance
                Automatically returns values converted to imperial if needed
        '''
        if param == 'distance':
            return self.uc.distance(self.distance)
        elif param == 'average':
            return self.uc.speed(self.average)
        elif param == 'upositive':
            return self.uc.height(self.upositive)
        elif param == 'unegative':
            return self.uc.height(self.unegative)
        elif param == 'maxspeed':
            return self.uc.speed(self.maxspeed)
        elif param == 'maxpace':
            return uc.float2pace(self.uc.pace(uc.pace_from_db(self.maxpace)))
        elif param == 'pace':
            return uc.float2pace(self.uc.pace(uc.pace_from_db(self.pace)))
        elif param == 'calories':
            return self.calories
        elif param == 'time':
            if not self.duration:
                return ""
            _hour ,_min, _sec = second2time(self.duration)
            if _hour == 0:
                return "%02d:%02d" % (_min, _sec)
            else:
                return "%0d:%02d:%02d" % (_hour, _min, _sec)
        else:
            logging.error("Unable to provide value for unknown parameter (%s) for activity", param)
            return None
