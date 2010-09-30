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

import locale
import sys
import os
import pygtk
import gobject
pygtk.require('2.0')
import gtk
import gtk.glade
from optparse import OptionParser
import logging
import logging.handlers
import traceback

from os import path

from record import Record
from waypoint import Waypoint
from extension import Extension
from importdata import Importdata
from plugins import Plugins
from profile import Profile

from gui.windowimportdata import WindowImportdata
from gui.windowmain import Main
from gui.warning import Warning
from lib.date import Date
from activitypool import ActivityPool
from lib.ddbb import DDBB

class pyTrainer:
    def __init__(self,filename = None, data_path = None):
        #Version constants
        self.version ="1.7.2_svn#632"
        self.DB_version = 3
        #Process command line options
        self.startup_options = self.get_options()
        #Setup logging
        self.set_logging(self.startup_options.log_level)
        logging.debug('>>')
        self.data_path = data_path
        self.date = Date()
        self.ddbb = None
        # Checking profile
        logging.debug('Checking configuration and profile...')
        self.profile = Profile(self.data_path,self)
        self.windowmain = None
        self.ddbb = DDBB(self.profile)
        logging.debug('connecting to DDBB')
        self.ddbb.connect()

        #Get user's DB version
        currentDB_version = self.profile.getValue("pytraining","DB_version")
        logging.debug("Current DB version: "+str(currentDB_version))
        # DB check can be triggered either via new version (mandatory) or as runtime parameter (--check)
        if self.startup_options.check: # User requested check
            self.sanityCheck()
        elif currentDB_version is None: # No stored DB version - check DB etc
            self.sanityCheck()
        elif self.DB_version > int(currentDB_version): # DB version expected is newer than user's version - check DB etc
            self.sanityCheck()
        else:
            logging.info('No sanity check requested')
        self.record = Record(data_path,self)
        pool_size = self.profile.getIntValue("pytraining","activitypool_size", default=1)
        self.activitypool = ActivityPool(self, size=pool_size)
        #preparamos la ventana principal
        self.windowmain = Main(data_path,self,self.version, gpxDir=self.profile.gpxdir)
        self.date = Date(self.windowmain.calendar)
        self.waypoint = Waypoint(data_path,self)
        self.extension = Extension(data_path, self)
        self.plugins = Plugins(data_path, self)
        self.importdata = Importdata(data_path, self, self.profile)
        self.loadPlugins()
        self.loadExtensions()
        self.windowmain.setup()
        self.windowmain.on_calendar_selected(None)
        self.refreshMainSportList()
        self.windowmain.run()
        logging.debug('<<')


    def get_options(self):
        '''
        Define usage and accepted options for command line startup

        returns: options - dict with option: value pairs
        '''
        usage = '''usage: %prog [options]

        For more help on valid options try:
           %prog -h '''
        parser = OptionParser(usage=usage)
        parser.set_defaults(log_level=logging.ERROR, validate=False, gm3=True, testimport=True, equip=False, newgraph=False)
        parser.add_option("-d", "--debug", action="store_const", const=logging.DEBUG, dest="log_level", help="enable logging at debug level")
        parser.add_option("-i", "--info", action="store_const", const=logging.INFO, dest="log_level", help="enable logging at info level")
        parser.add_option("-w", "--warn", action="store_const", const=logging.WARNING, dest="log_level", help="enable logging at warning level")
        parser.add_option("--valid", action="store_true", dest="validate", help="enable validation of files imported by plugins (details at info or debug logging level) - note plugin must support validation")
        parser.add_option("--check", action="store_true", dest="check", help="triggers database (only sqlite based) and configuration file sanity checks, adding fields if necessary. Backup of database is done before any change. Details at info or debug logging level")
        parser.add_option("--gmaps2", action="store_false", dest="gm3", help="Use old Google Maps API version (v2)")
        parser.add_option("--testimport", action="store_true", dest="testimport", help="EXPERIMENTAL: show new import functionality - for testing only USE AT YOUR OWN RISK")
        parser.add_option("--equip", action="store_false", dest="equip", help="EXPERIMENTAL: enable equipment management")
        parser.add_option("--newgraph", action="store_true", dest="newgraph", help="EXPERIMENTAL: new graphing approach")
        (options, args) = parser.parse_args()
        return options

    def set_logging(self,level):
        '''Setup rotating log file with customized format'''
        PATH = os.environ['HOME']+"/.pytrainer"
        if not os.path.exists(PATH):
            os.mkdir(PATH)
        LOG_FILENAME = PATH + "/log.out"
        rotHandler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=100000, backupCount=5)
        formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(module)s|%(funcName)s|%(message)s')
        rotHandler.setFormatter(formatter)
        logging.getLogger('').addHandler(rotHandler)
        self.set_logging_level(self.startup_options.log_level)

    def set_logging_level(self, level):
        '''Set level of information written to log'''
        logging.debug("Setting logger to level: "+ str(level))
        logging.getLogger('').setLevel(level)

    def quit(self):
        logging.debug('--')
        logging.info("Exit!")
        #self.webservice.stop()
        self.windowmain.gtk_main_quit()
        logging.shutdown()
        sys.exit() # Any nonzero value is considered “abnormal termination” by shells and the like

    def loadPlugins(self):
        logging.debug('>>')
        activeplugins = self.plugins.getActivePlugins()
        if (len(activeplugins)<1):
             logging.info("No active plugins")
        else:
             for plugin in activeplugins:
                txtbutton = self.plugins.loadPlugin(plugin)
                self.windowmain.addImportPlugin(txtbutton)
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
        print("Extension id: %s" % str(id))
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
        listSport = self.profile.getSportList()
        self.windowmain.updateSportList(listSport)
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
        elif view=="day":
             logging.debug('day view')
             record_list = self.record.getrecordList(date_selected)
             self.windowmain.actualize_dayview(record_list)
             #selected,iter = self.windowmain.recordTreeView.get_selection().get_selected()
        elif view=="week":
             logging.debug('week view')
             date_ini, date_end = self.date.getWeekInterval(date_selected, self.profile.prf_us_system)
             sport = self.windowmain.getSportSelected()
             record_list = self.record.getrecordPeriod(date_ini, date_end, sport)
             self.windowmain.actualize_weekview(record_list, date_ini, date_end)
        elif view=="month":
             logging.debug('month view')
             date_ini, date_end = self.date.getMonthInterval(date_selected)
             sport = self.windowmain.getSportSelected()
             record_list = self.record.getrecordPeriodSport(date_ini, date_end,sport)
             nameMonth, daysInMonth = self.date.getNameMonth(date_selected)
             self.windowmain.actualize_monthview(record_list, nameMonth)
             self.windowmain.actualize_monthgraph(record_list, daysInMonth)
        elif view=="year":
             logging.debug('year view')
             date_ini, date_end = self.date.getYearInterval(date_selected)
             sport = self.windowmain.getSportSelected()
             year = self.date.getYear(date_selected)
             record_list = self.record.getrecordPeriodSport(date_ini, date_end,sport)
             self.windowmain.actualize_yearview(record_list, year)
             self.windowmain.actualize_yeargraph(record_list)
        elif view=="listview":
            logging.debug('list view')
            self.refreshListView()
        else:
            print "Unknown view %s" % view
        logging.debug('<<')

    def refreshRecordGraphView(self, view):
        logging.debug('>>')
        logging.info('Working on '+view+' graph')
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
        logging.debug('Trying to show map for record '+str(id_record))
        self.windowmain.actualize_map(activity, full_screen)
        logging.debug('<<')

    def refreshListRecords(self):
        logging.debug('>>')
        #Refresh list view
        self.refreshListView()
        #Refresh list records
        date = self.date.getDate()
        record_list = self.record.getrecordList(date)
        self.windowmain.actualize_recordTreeView(record_list)
        record_list = self.record.getRecordDayList(date)
        self.windowmain.actualize_calendar(record_list)
        logging.debug('<<')

    def refreshAthleteView(self):
        logging.debug('>>')
        athletedata = {}
        athletedata['prf_name'] = self.profile.getValue("pytraining","prf_name")
        athletedata['prf_age'] = self.profile.getValue("pytraining","prf_age")
        athletedata['prf_height'] = self.profile.getValue("pytraining","prf_height")
        athletedata['history'] = (
            {'Date':'2010-01-01', 'Weight':88.8, 'BF':15.0, 'RestingHR':67, 'MaxHR':220},
            {'Date':'2010-02-01', 'Weight':89.8, 'BF':16.0, 'RestingHR':68, 'MaxHR':221},
            {'Date':'2010-03-01', 'Weight':99.1, 'BF':13.0, 'RestingHR':65, 'MaxHR':212},
            {'Date':'2010-04-01', 'Weight':79.5, 'BF':11.0, 'RestingHR':61, 'MaxHR':210},
            {'Date':'2010-05-01', 'Weight':67.2, 'BF':13.0, 'RestingHR':60, 'MaxHR':205},
            {'Date':'2010-06-01', 'Weight':83.8, 'BF':16.0, 'RestingHR':56, 'MaxHR':200},
        )
        self.windowmain.actualize_athleteview(athletedata)
        logging.debug('<<')

    def refreshListView(self):
        logging.debug('>>')
        record_list = self.record.getAllRecordList()
        self.windowmain.actualize_listview(record_list)
        logging.debug('<<')

    def refreshWaypointView(self,default_waypoint=None,redrawmap=1):
        logging.debug('>>')
        waypoint_list = self.waypoint.getAllWaypoints()
        self.windowmain.actualize_waypointview(waypoint_list,default_waypoint,redrawmap)
        logging.debug('<<')

    def searchListView(self,condition):
        logging.debug('>>')
        record_list = self.record.getRecordListByCondition(condition)
        self.windowmain.actualize_listview(record_list)
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
                txtbutton = self.plugins.loadPlugin(plugin)
                self.windowmain.addImportPlugin(txtbutton)
        logging.debug('<<')

    def setExtensions(self, before, after):
        logging.debug('>>')
        #Need to check for extensions that have been disabled (were active and now are not)
        for extension in before:
            if extension not in after:
                #disabled extension -> need to unload extension
                print "Need to disable extension %s " % extension
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

    def newRecord(self,title=None,distance=None,time=None,upositive=None,unegative=None,bpm=None,calories=None,date=None,comment=None):
        logging.debug('>>')
        list_sport = self.profile.getSportList()
        if date == None:
             date = self.date.getDate()
             self.record.newRecord(list_sport, date, title, distance, time, upositive, unegative, bpm, calories, comment)
        self.refreshListRecords()
        logging.debug('<<')

    def editRecord(self, id_record):
        logging.debug('>>')
        list_sport = self.profile.getSportList()
        logging.debug('id_record: '+str(id_record)+' | list_sport: '+str(list_sport))
        self.record.editRecord(id_record,list_sport)
        self.refreshListRecords()
        logging.debug('<<')

    def removeRecord(self, id_record, confirm = False):
        logging.debug('>>')
        if confirm:
             self.record.removeRecord(id_record)
        else:
             msg = _("Delete this database entry?")
             params = [id_record,True]
             warning = Warning(self.data_path,self.removeRecord,params)
             warning.set_text(msg)
             warning.run()
        self.refreshListRecords()
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
        from save import Save
        save = Save(self.data_path, self.record)
        save.run()
        logging.debug('<<')

    def editProfile(self):
        logging.debug('>>')
        self.profile.editProfile()
        self.activitypool.clear_pool()
        self.windowmain.setup()
        logging.debug('<<')

    def sanityCheck(self):
        """23.11.2009 - dgranda
        Checks database and configuration file
        args: none
        returns: none"""
        logging.debug('>>')
        logging.info('Checking database integrity')
        self.ddbb.checkDBIntegrity()
        logging.info('Setting DB version to: ' + str(self.DB_version))
        self.profile.setValue("pytraining","DB_version", str(self.DB_version))
        logging.debug('<<')
