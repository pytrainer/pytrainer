# -*- coding: utf-8 -*-

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

import sys
import os
import logging
import traceback
import warnings

import gi
gi.require_version('Gtk', '3.0')

from pytrainer.lib.date import DateRange
from .upgrade.data import initialize_data
from .environment import Environment
from .record import Record
from .version import version
from .waypoint import WaypointService
from .extension import Extension
from .importdata import Importdata
from .plugins import Plugins
from .profile import Profile
from pytrainer.core.sport import SportService
from .athlete import Athlete
from .stats import Stats

from .gui.windowmain import Main
from .gui.warning import Warning
from .lib.date import Date, getNameMonth
from pytrainer.core.activity import ActivityService
from .lib.ddbb import DDBB
from .lib.uc import UC

class pyTrainer:

    def __init__(self, options):
        self.version = version
        self.startup_options = options
        self.environment = Environment()
        self.environment.clear_temp_dir()
        logging.debug('>>')
        logging.info("pytrainer version %s", self.version)
        self.data_path = self.environment.data_path

        # Checking profile
        logging.debug('Checking configuration and profile...')
        self.profile = Profile()
        # Write the default config to disk
        self.profile.saveProfile()
        self.uc = UC()
        self.profilewindow = None
        self.ddbb = DDBB(self.profile.sqlalchemy_url)
        logging.debug('connecting to DDBB')
        self.ddbb.connect()

        logging.info('Checking if some upgrade action is needed...')
        initialize_data(self.ddbb, self.environment.conf_dir)

        # Loading shared services
        logging.debug('Loading sport service...')
        self._sport_service = SportService(self.ddbb)
        logging.debug('Loading record service...')
        self.record = Record(self._sport_service, self.environment.data_path, self)
        logging.debug('Loading athlete service...')
        self.athlete = Athlete(self.environment.data_path, self)
        logging.debug('Loading stats service...')
        self.stats = Stats(self)
        logging.debug('Initializing activity pool...')
        pool_size = self.profile.getIntValue("pytraining","activitypool_size", default=1)
        self.activitypool = ActivityService(self, size=pool_size)

        #Loading main window
        self.windowmain = None
        logging.debug('Loading main window...')
        self.windowmain = Main(self._sport_service, self.environment.data_path, self, self.version, gpxDir=self.profile.gpxdir)

        # Select initial date depending on user's preference
        self.selectInitialDate()
        
        logging.debug('Loading waypoint service...')
        self.waypoint = WaypointService(self.environment.data_path, self)
        logging.debug('Loading extension service...')
        self.extension = Extension(self.environment.data_path, self)
        logging.debug('Loading plugins service...')
        self.plugins = Plugins(self.environment.data_path, self)
        self.importdata = Importdata(self._sport_service, self.environment.data_path, self, self.profile)
        logging.debug('Loading plugins...')
        self.loadPlugins()
        logging.debug('Loading extensions...')
        self.loadExtensions()
        logging.debug('Setting values for graphs, maps and waypoint editor...')
        self.windowmain.setup()
        self.windowmain.on_calendar_selected(None)
        logging.debug('Refreshing sport list... is this needed?')
        self.refreshMainSportList()
        logging.debug('Launching main window...')
        self.windowmain.run()
        logging.debug('<<')

    def quit(self):
        logging.debug('--')
        logging.info("Exit!")
        #self.webservice.stop()
        self.windowmain.gtk_main_quit()
        logging.shutdown()
        sys.exit() # Any nonzero value is considered "abnormal termination" by shells and the like

    def selectInitialDate(self):
        logging.debug('>>')
        # self.windowmain.calendar comes from SimpleGladeApp initialisation, not really sure how... :?
        self.date = Date(self.windowmain.calendar)
        if self.profile.getValue("pytraining","prf_startscreen") == "last_entry":
            logging.info("User selection is to display last entry in start screen")
            last_entry_date = self.record.getLastRecordDateString()
            try:
                logging.info("Last activity found on %s" %last_entry_date)
                self.date.setDate(last_entry_date)
            except:
                logging.error("No data available regarding last activity date. Default date will be today")
                logging.debug("Traceback: %s" % traceback.format_exc())
        else:
            logging.info("User selection is to display current day in start screen")
        logging.debug('Setting date to %s' % self.date.getDate().strftime("%Y-%m-%d"))
        logging.debug('<<')

    def loadPlugins(self):
        logging.debug('>>')
        activeplugins = self.plugins.getActivePlugins()
        if (len(activeplugins)<1):
             logging.info("No active plugins")
        else:
             for plugin in activeplugins:
                # From version 1.10 on all file imports are managed via File -> import wizard
                # Only showing garmintools_full and garmin-hr in 'File' dropdown
                plugin_name = os.path.basename(plugin)
                if (plugin_name == "garmintools_full" or plugin_name == "garmin-hr"):
                    warnings.warn('Attempted to enable an unsupported plugin %s' % plugin_name,
                                  UserWarning)
                else:
                    logging.debug('From version 1.10 on, file import plugins are managed via File -> Import. Not displaying plugin ' + plugin_name)
        logging.debug('<<')

    def loadExtensions(self):
        logging.debug('>>')
        activeextensions = self.extension.getActiveExtensions()
        if (len(activeextensions)<1):
             logging.info("No active extensions")
        else:
             for extension in activeextensions:
                txtbutton = self.extension.loadExtension(extension)
                self.windowmain.addExtension(txtbutton)
        logging.debug('<<')

    def runPlugin(self,widget,pathPlugin):
        logging.debug('>>')
        self.pluginClass = self.plugins.importClass(pathPlugin)
        pluginFiles = self.pluginClass.run()
        if pluginFiles is not None:
            logging.debug("Plugin returned %d files" % (len(pluginFiles)) )
            #process returned GPX files
            for (pluginFile, sport) in pluginFiles:
                if os.path.isfile(pluginFile):
                    logging.info('File exists. Size: %d. Sport: %s' % (os.path.getsize(pluginFile), sport))
                    if self.record.importFromGPX(pluginFile, sport) is None:
                        logging.error("Error importing file "+pluginFile)
                else:
                    logging.error('File '+pluginFile+' not valid')
        else:
            logging.debug("No files returned from Plugin")
        self.refreshListRecords()
        self.refreshGraphView("day")
        logging.debug('<<')

    def runExtension(self,extension,id):
        logging.debug('>>')
        activity = self.activitypool.get_activity(id)
        txtbutton,pathExtension,type = extension
        self.extensionClass = self.extension.importClass(pathExtension)
        self.extensionClass.run(id, activity)
        #if type == "record":
        #   #Si es record le tenemos que crear el googlemaps, el gpx y darle el id de la bbdd
        #   alert = self.extension.runExtension(pathExtension,id)

        logging.debug('<<')

    def refreshMainSportList(self):
        logging.debug('>>')
        sports = self._sport_service.get_all_sports()
        self.windowmain.updateSportList(sports)
        logging.debug('<<')

    def refreshGraphView(self, view, sport=None):
        logging.debug('>>')
        if self.windowmain is None:
            logging.debug("First call to refreshGraphView")
            logging.debug('<<')
            return
        date_selected = self.date.getDate()
        if view=="record":
             logging.debug('record view')
             if self.windowmain.recordview.get_current_page()==0:
                self.refreshRecordGraphView("info")
             elif self.windowmain.recordview.get_current_page()==1:
                self.refreshRecordGraphView("graphs")
             elif self.windowmain.recordview.get_current_page()==2:
                self.refreshRecordGraphView("map")
             elif self.windowmain.recordview.get_current_page()==3:
                self.refreshRecordGraphView("heartrate")
             elif self.windowmain.recordview.get_current_page()==4:
                self.refreshRecordGraphView("analytics")
        elif view=="day":
             logging.debug('day view')
             self.windowmain.actualize_dayview(date_selected)
        elif view=="week":
             logging.debug('week view')
             date_range = DateRange.for_week_containing(date_selected)
             self.windowmain.actualize_weekview(date_range)
        elif view=="month":
             logging.debug('month view')
             date_range = DateRange.for_month_containing(date_selected)
             nameMonth, daysInMonth = getNameMonth(date_selected)
             self.windowmain.actualize_monthview(date_range, nameMonth, daysInMonth)
        elif view=="year":
             logging.debug('year view')
             date_range = DateRange.for_year_containing(date_selected)
             self.windowmain.actualize_yearview(date_range, date_selected.year)
        elif view=="listview":
            logging.debug('list view')
            self.refreshListView()
        elif view=="athlete":
            logging.debug('athlete view')
            self.windowmain.on_athleteview_activate()
        elif view=="stats":
            logging.debug('stats view')
            self.windowmain.on_statsview_activate()
        else:
            logging.error("Unknown view %s", view)
        logging.debug('<<')
        
    def refreshRecordGraphView(self, view, id_record=None):
        logging.debug('>>')
        logging.info('Working on '+view+' graph')
        if id_record is not None:
            #Refresh called for a specific record
            #Select correct record in treeview
            model = self.windowmain.recordTreeView.get_model()
            #Loop through all records in treeview looking for the correct one to highlight
            for i,row in enumerate(model):
                if row[0] == id_record:
                    self.windowmain.recordTreeView.set_cursor(i)
        else:
            selected,iter = self.windowmain.recordTreeView.get_selection().get_selected()
            if iter:
                id_record = selected.get_value(iter,0)
            else:
                id_record = None
                view="info"
        activity = self.activitypool.get_activity(id_record)
        if view=="info":
            self.windowmain.actualize_recordview(activity)
        if view=="graphs":
            self.windowmain.actualize_recordgraph(activity)
        if view=="map":
             self.refreshMapView()
        if view=="heartrate":
             self.windowmain.actualize_heartrategraph(activity)
             self.windowmain.actualize_hrview(activity)
        if view=="analytics":
             self.windowmain.actualize_analytics(activity)
        logging.debug('<<')

    def refreshMapView(self, full_screen=False):
        logging.debug('>>')
        if self.windowmain is None:
            logging.debug('Called before windowmain initialisation')
            logging.debug('<<')
            return
        selected,iter = self.windowmain.recordTreeView.get_selection().get_selected()
        id_record = selected.get_value(iter,0)
        activity = self.activitypool.get_activity(id_record)
        logging.debug('Trying to show map for record %s', id_record)
        self.windowmain.actualize_map(activity, full_screen)
        logging.debug('<<')

    def refreshListRecords(self):
        logging.debug('>>')
        #Refresh list records
        date = self.date.getDate()
        if self.windowmain.activeSport:
            sport = self._sport_service.get_sport_by_name(self.windowmain.activeSport)
        else:
            sport = None
        self.windowmain.actualize_recordTreeView(date)
        #Mark the monthly calendar to show which days have activity?
        record_list = self.record.getRecordDayList(date, sport)
        self.windowmain.actualize_calendar(record_list)
        logging.debug('<<')

    def refreshAthleteView(self):
        logging.debug('>>')
        self.athlete.refresh()
        self.windowmain.actualize_athleteview(self.athlete)
        logging.debug('<<')

    def refreshStatsView(self):
        logging.debug('>>')
        self.stats.refresh()
        self.windowmain.actualize_statsview(self.stats, self.activitypool.get_all_activities())
        logging.debug('<<')

    def refreshListView(self,condition=None):
        logging.debug('>>')
        record_list = self.record.getRecordListByCondition(condition)
        self.windowmain.actualize_listview(record_list)
        logging.debug('<<')

    def refreshWaypointView(self,default_waypoint=None,redrawmap=1):
        logging.debug('>>')
        waypoint_list = self.waypoint.getAllWaypoints()
        self.windowmain.actualize_waypointview(waypoint_list,default_waypoint,redrawmap)
        logging.debug('<<')

    def editExtensions(self):
        logging.debug('>>')
        before = self.extension.getActiveExtensions()
        self.extension.manageExtensions()
        after = self.extension.getActiveExtensions()
        self.setExtensions(before, after)
        logging.debug('<<')

    def importData(self):
        logging.debug('>>')
        activeplugins_before = self.plugins.getActivePlugins()
        self.importdata.runImportdata()
        activeplugins_after = self.plugins.getActivePlugins()
        #Need to check for plugins that have been disabled (were active and now are not)
        self.setMenuPlugins(activeplugins_before, activeplugins_after)
        self.refreshListRecords()
        self.refreshGraphView(self.windowmain.selected_view)
        logging.debug('<<')

    def editGpsPlugins(self):
        logging.debug('>>')
        activeplugins_before = self.plugins.getActivePlugins()
        self.plugins.managePlugins()
        activeplugins_after = self.plugins.getActivePlugins()
        #Need to check for plugins that have been disabled (were active and now are not)
        self.setMenuPlugins(activeplugins_before, activeplugins_after)
        logging.debug('<<')

    def setMenuPlugins(self, activeplugins_before, activeplugins_after):
        logging.debug('>>')
        #Need to check for plugins that have been disabled (were active and now are not)
        for plugin in activeplugins_before:
            if plugin not in activeplugins_after:
                #disabled plugin -> need to unload plugin
                txtbutton = self.plugins.loadPlugin(plugin)
                self.windowmain.removeImportPlugin(txtbutton)
        #Need to check for plugins that have been enabled (were not active and now are)
        for plugin in activeplugins_after:
            if plugin not in activeplugins_before:
                #new active plugin -> need to load plugin
                plugin_name = os.path.basename(plugin)
                if (plugin_name == "garmintools_full" or plugin_name == "garmin-hr"):
                    warnings.warn('Attempted to enable an unsupported plugin %s' % plugin_name,
                                  UserWarning)
                else:
                    logging.debug('From version 1.10 on file import plugins are managed via File -> Import. Not displaying plugin ' + plugin_name)
        logging.debug('<<')

    def setExtensions(self, before, after):
        logging.debug('>>')
        #Need to check for extensions that have been disabled (were active and now are not)
        for extension in before:
            if extension not in after:
                #disabled extension -> need to unload extension
                logging.error("Need to disable extension %s", extension)
                txtbutton = self.extension.loadExtension(extension)
                self.windowmain.removeExtension(txtbutton)
        #Need to check for plugins that have been enabled (were not active and now are)
        for extension in after:
            if extension not in before:
                #new active extension -> need to load extension
                logging.debug("Enabling extension %s " % extension)
                txtbutton = self.extension.loadExtension(extension)
                self.windowmain.addExtension(txtbutton)
        logging.debug('<<')

    def newRecord(self,title=None,distance=None,time=None,upositive=None,unegative=None,bpm=None,calories=None,comment=None,view=None):
        logging.debug('>>')
        date = self.date.getDate()
        self.record.newRecord(date, title, distance, time, upositive, unegative, bpm, calories, comment)
        self.refreshListRecords()
        if view is not None:
            self.refreshGraphView(view)
        logging.debug('<<')

    def editRecord(self, id_record, view=None):
        logging.debug("Editing record with id: '%s'", id_record)
        self.record.editRecord(id_record)
        self.refreshListRecords()
        if view is not None:
            self.refreshGraphView(view)
        logging.debug('<<')

    def removeRecord(self, id_record, confirm = False, view=None):
        logging.debug('>>')
        if confirm:
             activity = self.activitypool.get_activity(id_record)
             self.activitypool.remove_activity_from_db(activity)
        else:
             msg = _("Delete this database entry?")
             params = [id_record,True]
             warning = Warning(self.data_path,self.removeRecord,params)
             warning.set_text(msg)
             warning.run()
        self.refreshListRecords()
        if view is not None:
            self.refreshGraphView(view)
        logging.debug('<<')

    def removeWaypoint(self,id_waypoint, confirm = False):
        logging.debug('>>')
        if confirm:
             self.waypoint.removeWaypoint(id_waypoint)
             self.refreshWaypointView()
        else:
             msg = _("Delete this waypoint?")
             params = [id_waypoint,True]
             warning = Warning(self.data_path,self.removeWaypoint,params)
             warning.set_text(msg)
             warning.run()
        logging.debug('<<')

    def updateWaypoint(self,id_waypoint,lat,lon,name,desc,sym):
        logging.debug('>>')
        self.waypoint.updateWaypoint(id_waypoint,lat,lon,name,desc,sym)
        self.refreshWaypointView(id_waypoint)
        logging.debug('<<')

    def exportCsv(self):
        logging.debug('>>')
        from .save import Save
        save = Save(self.ddbb)
        save.run()
        logging.debug('<<')

    def editProfile(self):
        logging.debug('>>')
        from .gui.windowprofile import WindowProfile
        self.profile.refreshConfiguration()
        if self.profilewindow is None:
            self.profilewindow = WindowProfile(self._sport_service, self.data_path, self.profile, pytrainer_main=self)
            logging.debug("setting data values")
            self.profilewindow.setValues(self.profile.configuration)
            self.profilewindow.run()
            self.profilewindow = None
        else:
            self.profilewindow.setValues(self.profile.configuration)
            self.profilewindow.present()
        self.profile.refreshConfiguration()

        self.activitypool.clear_pool()
        self.windowmain.setup()
        logging.debug('<<')
