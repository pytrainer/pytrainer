#!/usr/bin/env python
# -*- coding: utf-8 -*-

from SimpleGladeApp import SimpleBuilderApp
import gtk
import gobject
import os, glob, sys
import StringIO
import logging
import types
from lxml import etree
import csv
import locale

from pytrainer.plugins import Plugins
from pytrainer.gui.dialogs import fileChooserDialog
from pytrainer.lib.date import getDateTime

class WindowImportdata(SimpleBuilderApp):
    def __init__(self, sport_service, data_path = None, parent=None, config=None, pytrainer_main=None):
        self._sport_service = sport_service
        self.data_path = data_path
        self.parent = parent
        self.pytrainer_main = pytrainer_main
        self.configuration = config
        self.activities_store = None # gtk.ListStore containing gtk.TreeModelRow, see build_activities_tree_view
        self.files_store = None # gtk.ListStore containing gtk.TreeModelRow, see build_files_tree_view
        self.processClasses = []
        self.plugins = Plugins(data_path, self.parent.parent)
        SimpleBuilderApp.__init__(self, "importdata.ui")

    def new(self):
        logging.debug(">>")
        try:
            self.defaulttab = self.configuration.getValue("pytraining","import_default_tab")
            self.defaulttab = int(self.defaulttab)
        except Exception as e:
            logging.debug("Exception: %s", str(e))
            self.defaulttab = 0
        self.auto_launch = self.configuration.getValue("pytraining","auto_launch_file_selection")
        if self.auto_launch == "True":
            self.auto_launch = True
        else:
            self.auto_launch = False
        logging.debug("Default tab: %s, Auto launch: %s" % (str(self.defaulttab), str(self.auto_launch)))
        self.init_all_tabs()
        self.notebookMainTabs.set_current_page(self.defaulttab)
        self.init_tab(self.defaulttab, first=True)          #TODO fix so dont need to re-call init_tab
        logging.debug("<<")

    def init_all_tabs(self):
        logging.debug(">>")
        tabs = (0,1,2,3,4)
        for tab in tabs:
            self.init_tab(tab)

    def init_tab(self, page, first=False):
        ''' Initialise tab '''
        logging.debug(">>")
        logging.debug("page: %d first: %s" % (page, first))
        if page == 0:
            #'Import from GPS Device' tab
            self.init_gpsdevice_tab()
        elif page == 1:
            #'Import from File' tab
            self.init_file_tab(first)
        elif page == 2:
            #'Plugins' tab
            self.init_plugins_tab()
        elif page == 3:
            #'Options' tab
            self.init_options_tab()
        elif page == 4:
            #'CSV Import' tab
            self.init_csvimport_tab()
        else:
            #unknown tab
            logging.error("Unknown page %d passed to init_tab" % page)

    def updateStatusbar(self, statusbar, text, context_id = None):
        ''' Help function to set the text of the statusbar '''
        logging.debug("Setting statusbar %s to %s" % (statusbar.get_name(), text) )
        if context_id is None:
            context_id = statusbar.get_context_id(text)
        statusbar.push(context_id, text)
        return context_id

    def init_gpsdevice_tab(self):
        logging.debug(">>")
        logging.error("GPS Device import not yet implemented")
        logging.debug("<<")
        return

    def init_file_tab(self, first=False):
        logging.debug(">>")
        self.updateStatusbar(self.statusbarImportFile, _("No file selected") )
        self.processClasses = []
        if self.activities_store is None:
            self.activities_store = self.build_activities_tree_view()
        else:
            self.activities_store.clear()
        if self.files_store is None:
            self.files_store = self.build_files_tree_view()
        else:
            self.files_store.clear()
        self.buttonRemoveSelectedFiles.set_sensitive(0)
        self.buttonFileImport.set_sensitive(0)
        if first and self.auto_launch:
            while gtk.events_pending(): # This allows the GUI to update
                gtk.main_iteration()    # before completion of this entire action
            logging.debug("autolaunch active")
            self.buttonSelectFiles.clicked()
        logging.debug(">>")
        return

    def init_plugins_tab(self):
        logging.debug(">>")
        #Remove components in vbox - in case of re-detection
        for child in self.vboxPlugins.get_children():
            if isinstance(child, gtk.Table):
                self.vboxPlugins.remove(child)
        pluginList = self.plugins.getPluginsList()
        logging.debug(pluginList)
        for plugin in pluginList:
            #Store plugin details
            pluginClass = plugin[0]
            pluginName = plugin[1]
            pluginDescription = plugin[2]
            #Build frame with name and description
            pluginFrame = gtk.Frame(label="<b>"+pluginName+"</b>")
            pluginFrameLabel = pluginFrame.get_label_widget()
            pluginFrameLabel.set_use_markup(True)
            description = gtk.Label("<small>"+pluginDescription+"</small>")
            description.set_alignment(0,0)
            description.set_use_markup(True)
            description.set_line_wrap(True)
            pluginFrame.add(description)
            #Get plugin information
            name,description,status = self.plugins.getPluginInfo(pluginClass)
            #Create labels and buttons
            configButton = gtk.Button(label=_("Configure"))
            #Connect button handlers
            configButton.connect('clicked', self.on_pluginsButton_Configure_clicked, pluginClass)
            if status == 0 or status == "0":
                #Plugin disabled
                pluginFrame.set_sensitive(0)
                statusLabel = gtk.Label(_("Disabled"))
            else:
                statusLabel = gtk.Label(_("Enabled"))

            #Create a table for the frame and button
            pluginTable = gtk.Table()
            pluginTable.attach(pluginFrame, 0, 1, 0, 1, xoptions=gtk.EXPAND|gtk.FILL, xpadding=5)
            pluginTable.attach(statusLabel, 1, 2, 0, 1, xoptions=gtk.FILL, yoptions=gtk.SHRINK, xpadding=5, ypadding=5)
            pluginTable.attach(configButton, 2, 3, 0, 1, xoptions=gtk.FILL, yoptions=gtk.SHRINK, xpadding=5, ypadding=5)
            #Add frame to tab
            self.vboxPlugins.pack_start(pluginTable, expand=False, fill=False, padding=5)
        self.win_importdata.show_all()
        logging.debug("<<")
        return

    def init_options_tab(self):
        logging.debug(">>")
        logging.debug("Default tab %s" % str(self.defaulttab) )
        #Set correct radiobutton based on saved preference
        if self.defaulttab == 1:
            self.radiobuttonFile.set_active(1)
            self.checkbuttonAutoLaunch.set_sensitive(1)
        elif self.defaulttab == 2:
            self.radiobuttonPlugins.set_active(1)
        else:
            self.radiobuttonTabGPSDevice.set_active(1)
        if self.auto_launch:
            self.checkbuttonAutoLaunch.set_active(1)
        logging.debug("<<")
        return

    def init_csvimport_tab(self):
        logging.debug(">>")
        #Populate Force Sport to combobox
        sport_list = self._sport_service.get_all_sports()
        #Remove placeholder item (needed to ensure correct model for combobox)
        self.comboCSVForceSport.remove_text(0)
        for sport in sport_list:
            logging.debug('Adding sport: %s' % sport.name)
            self.comboCSVForceSport.append_text(sport.name)
        self.comboCSVForceSport.set_active(0)
        logging.debug("<<")
        return

    def detect_tools(self):
        '''
            Iterate through all tool files from import directory
            Each file contains information on a particular tool
            and knows how to determine if the tool is present on the system
            and what configuration options are needed for the tool

            Currently displays the tool info and config grayed out if tool is not present
        '''
        logging.debug('>>')
        self.updateStatusbar(self.statusbarDevice, _("Checking for tools"))
        #Remove all components in vbox - in case of re-detection
        for child in self.vboxImportTools.get_children():
            self.vboxImportTools.remove(child)
        #Get import tool_* files
        fileList = glob.glob(self.data_path+"imports/tool_*.py")
        logging.debug("Tools filelist: %s" % fileList)
        for toolFile in fileList:
            index = fileList.index(toolFile)
            directory, filename = os.path.split(toolFile)
            filename = filename.rstrip('.py')
            classname = filename.lstrip('tool_')
            #Import module
            sys.path.insert(0, self.data_path+"import")
            module = __import__(filename)
            toolMain = getattr(module, classname)
            #Instantiate module
            toolClass = toolMain(self.parent, self.data_path)
            #Get info from class
            toolName = toolClass.getName()
            toolTable = gtk.Table()
            toolFrame = gtk.Frame(label=toolName)
            toolFrame.add(toolTable)
            if toolClass.isPresent():
                version = gtk.Label("Version: " + toolClass.getVersion())
                version.set_alignment(0,0)
                if toolClass.deviceExists():
                    deviceExists = gtk.Label(_("GPS device found") )
                    deviceExists.set_alignment(0,0)
                else:
                    deviceExists = gtk.Label(_("GPS device <b>not</b> found"))
                    deviceExists.set_alignment(0,0)
                    deviceExists.set_use_markup(True)
                toolTable.attach(version, 0, 1, 0, 1, xoptions=gtk.EXPAND|gtk.FILL, xpadding=5)
                toolTable.attach(deviceExists, 0, 1, 1, 2, xoptions=gtk.EXPAND|gtk.FILL, xpadding=5)
                toolFrame.set_sensitive(1)
            else:
                info = gtk.Label(_("This tool was not found on the system") )
                info.set_alignment(0,0.5)
                location = gtk.LinkButton(toolClass.getSourceLocation(), toolName +_(" Homepage"))
                info.set_sensitive(0)
                toolTable.attach(info, 0, 1, 0, 1, xoptions=gtk.EXPAND|gtk.FILL, xpadding=5)
                toolTable.attach(location, 1, 2, 0, 1, xoptions=gtk.EXPAND|gtk.FILL, xpadding=5)
                #toolFrame.set_sensitive(0)
            self.vboxImportTools.pack_start(toolFrame, expand=False, fill=False, padding=5)
        self.win_importdata.show_all()
        logging.debug('<<')

    def validateFile(self, import_filename):
        '''
            Iterate through all supported types of file by reading processing files from import directory
            Each processing file understands one type of file

            If a processing file is found that recognises the selected file:
                 returns the instantiated class
            otherwise:
                 returns None
        '''
        logging.debug('>>')
        self.updateStatusbar(self.statusbarImportFile, _("Checking file type for: ") + import_filename)
        #Get imports files_* files
        fileList = glob.glob(self.data_path+"imports/file_*.py")
        fileList.sort()
        logging.debug("File filelist: %s" % fileList)
        for processingFile in fileList:
            directory, filename = os.path.split(processingFile)
            filename = filename.rstrip('.py')
            logging.debug("Trying: %s" % filename)
            classname = filename.lstrip('file_')
            #Import module
            sys.path.insert(0, self.data_path + "imports")
            module = __import__(filename)
            processMain = getattr(module, classname)
            #Instantiate module
            processClass = processMain(self.parent, self.data_path)
            isValid = processClass.testFile(import_filename)
            if isValid:
                logging.debug('<<')
                return processClass
            else:
                processClass = None
        logging.debug('<<')
        return processClass

    def build_files_tree_view(self):
        ''' Build tree view to hold files from which the activities are read '''
        logging.debug('>>')
        store = gtk.ListStore(  gobject.TYPE_STRING,
                                gobject.TYPE_BOOLEAN,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING, )
        column_names=["id", "", _("File"), _("Type"), _("Activities")]
        for column_index, column_name in enumerate(column_names):
            if column_index == 1:
                #Add button column
                self.renderer1 = gtk.CellRendererToggle()
                self.renderer1.set_property('activatable', True)
                self.renderer1.connect( 'toggled', self.treeviewImportFiles_toggled_checkbox, store )
                column = gtk.TreeViewColumn(column_name, self.renderer1 )
                column.add_attribute( self.renderer1, "active", column_index)
                column.set_sort_column_id(-1)
            else:
                #Add other columns
                column = gtk.TreeViewColumn(column_name, gtk.CellRendererText(), text=column_index)
                column.set_sort_column_id(column_index)
            if column_name == "id":
                column.set_visible(False)
            column.set_resizable(True)
            self.treeviewImportFiles.append_column(column)
        self.treeviewImportFiles.set_headers_clickable(True)
        self.treeviewImportFiles.set_model(store)
        logging.debug('<<')
        return store

    def build_activities_tree_view(self):
        ''' Build tree view to hold activities that can be selected for import '''
        logging.debug('>>')
        store = gtk.ListStore(  gobject.TYPE_STRING,
                                gobject.TYPE_BOOLEAN,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING,
                                gobject.TYPE_BOOLEAN )
        column_names=["id", "", _("Start Time"), _("Distance"), _("Duration"), _("Sport"), _("Notes"), "file_id", "in_db"]
        for column_index, column_name in enumerate(column_names):
            if column_index == 1:
                #Add checkbox column
                self.renderer1 = gtk.CellRendererToggle()
                self.renderer1.set_property('activatable', True)
                self.renderer1.connect( 'toggled', self.treeviewImportEvents_toggled_checkbox, store )
                column = gtk.TreeViewColumn(column_name, self.renderer1 )
                column.add_attribute( self.renderer1, "active", column_index)
                column.set_sort_column_id(-1)
                column.connect('clicked', self.treeviewImportEvents_header_checkbox, store)
            else:
                #Add other columns
                column = gtk.TreeViewColumn(column_name, gtk.CellRendererText(), text=column_index)
                column.set_sort_column_id(column_index)
            if column_name == "id" or column_name == "file_id" or column_name == "in_db":
                column.set_visible(False)
            column.set_resizable(True)
            self.treeviewImportEvents.append_column(column)
        self.treeviewImportEvents.set_headers_clickable(True)
        self.treeviewImportEvents.set_model(store)
        logging.debug('<<')
        return store

    def checkTreestoreForSelection(self, store):
        '''
            Function iterates over store checking if any items are selected
            returns True if at least one item is selected, False otherwise
            Checks item in position 1 only
        '''
        for item in store:
            if item[1]:
                return True
        return False

    def treeviewImportFiles_toggled_checkbox(self, cell, path, store):
        '''
            Sets the state of the checkbox to true or false.
        '''
        store[path][1] = not store[path][1]
        self.buttonRemoveSelectedFiles.set_sensitive(self.checkTreestoreForSelection(store))

    def treeviewImportEvents_toggled_checkbox(self, cell, path, store):
        '''
            Sets the state of the checkbox to true or false.
        '''
        store[path][1] = not store[path][1]
        self.buttonFileImport.set_sensitive(self.checkTreestoreForSelection(store))

    def treeviewImportEvents_setCheckboxes(self, state):
        '''
            Sets or unsets all checkboxes
        '''
        if self.activities_store is None or len(self.activities_store) == 0:
            return
        for item in self.activities_store:
            item[1] = state
        if state:
            self.buttonFileImport.set_sensitive(1)
        else:
            self.buttonFileImport.set_sensitive(0)

    def saveOptions(self):
        '''
            Save options selected in options tab
        '''
        self.autoLaunchFileSelection = "False"
        #Default tab option
        if self.radiobuttonTabGPSDevice.get_active():
            self.defaulttab = "0"
        elif self.radiobuttonFile.get_active():
            self.defaulttab = "1"
            if self.checkbuttonAutoLaunch.get_active():
                self.autoLaunchFileSelection = "True"
        elif self.radiobuttonPlugins.get_active():
            self.defaulttab = "2"
        logging.debug("Saving default tab: %s, auto launch: %s" % (str(self.defaulttab), str(self.autoLaunchFileSelection)))
        self.configuration.setValue("pytraining","import_default_tab",self.defaulttab)
        self.configuration.setValue("pytraining","auto_launch_file_selection",self.autoLaunchFileSelection)

    def removeSelectedFiles(self):
        '''
            Function to determine which files are selected
            * remove them from the list
            * remove the associated activities from the list also
        '''
        if self.files_store is None:
            return
        file_index = 0
        file_iters = []
        activity_iters = []
        for item in self.files_store:
            if item[1] is True: #Checkbox is True, file for removal
                file_id = item[0]
                activity_index = 0
                for activity in self.activities_store:
                    if activity[7] == file_id: #Activity relates to file to be removed
                        activity_iters.append(self.activities_store.get_iter(activity_index))
                    activity_index += 1
                file_iters.append( self.files_store.get_iter(file_index))
            file_index += 1
        logging.debug("Removing %d activities from activity tree view" % len(activity_iters) )
        for activity_iter in activity_iters:
            self.activities_store.remove(activity_iter)
        self.buttonFileImport.set_sensitive(self.checkTreestoreForSelection(self.activities_store)) #Set correct state for import button
        logging.debug("Removing %d files from file tree view" % len(file_iters) )
        for file_iter in file_iters:
            self.files_store.remove(file_iter)

    def getSelectedActivities(self):
        """
            Function to determine which activities are selected

            Returns array of the ids of the selected activities
        """
        selectedActivities = []
        if self.activities_store is None:
            logging.debug("activities_store is empty")
            return None
        for item in self.activities_store:
            if item[1] is True: #Checkbox is True (selected)
                logging.debug("Added activity %s to selected list" % item)
                file_id = int(item[7])
                activity_id = item[0]
                start_time = item[2]
                distance = item[3]
                duration = item[4]
                sport = item[5]
                gpx_file = self.processClasses[file_id].getGPXFile(activity_id, file_id)[1]
                in_db = item[8]
                selectedActivities.append((activity_id, start_time, distance, duration, sport, gpx_file, file_id, in_db))
        logging.debug("Found %d selected activities to import" % len(selectedActivities))
        return selectedActivities

    def importSelectedActivities(self, activities):
        """
            Function to import selected activity
        """
        logging.debug("Checking if activities are already present in database...")
        for activity in activities:
            if activity[7]:
                logging.debug("Activity from %s (%s) already in database. Skipping import." % (activity[1], activity[5]))
                activities.remove(activity)
                self.updateActivity(activity[0], activity[6], status = False)

        if len(activities) > 0:
            logging.debug("Importing %d activities" % len(activities))
            result = self.pytrainer_main.record.newMultiRecord(activities)
            for activity in result:
                if "db_id" in activity.keys() and type(activity["db_id"]) is types.IntType:
                    #Activity imported correctly
                    duration = "%0.0f:%0.0f:%02.0f" % (float(activity["rcd_time"][0]), float(activity["rcd_time"][1]), float(activity["rcd_time"][2]))
                    self.updateActivity(activity["activity_id"], 
                                        activity["file_id"],
                                        status = False,
                                        notes = _("Imported into database"),
                                        sport = activity["rcd_sport"],
                                        distance = activity["rcd_distance"],
                                        duration = duration,
                                        in_db = True)
        else:
            logging.debug("No activities to import")
        return len(activities)

    def updateActivity(self, activityID, file_id, status = None, notes = None, sport = None, distance = None, duration = None, in_db = None):
        path = 0
        for item in self.activities_store:
            if item[0] == activityID and item[7] == str(file_id):
                if status is not None:
                    self.activities_store[path][1] = status
                if notes is not None:
                    self.activities_store[path][6] = notes
                if sport is not None:
                    self.activities_store[path][5] = sport
                if distance is not None:
                    self.activities_store[path][3] = distance
                if duration is not None:
                    self.activities_store[path][4] = duration
                if in_db is not None:
                    self.activities_store[path][8] = in_db
            path +=1

    def close_window(self):
        logging.debug('--')
        self.win_importdata.hide()
        self.quit()

    ############################
    ## Window signal handlers ##
    ############################

    def on_radiobuttonFile_toggled(self, *args):
        print "radio button toggled"

    def on_pluginsButton_Configure_clicked(self, button, pluginClass):
        '''
            Handler for plugin Buttons
        '''
        name,description,status = self.plugins.getPluginInfo(pluginClass)
        prefs = self.plugins.getPluginConfParams(pluginClass)

        self.prefwindow = gtk.Window()
        self.prefwindow.set_border_width(20)
        self.prefwindow.set_title(_("%s settings" %name))

        table = gtk.Table(1,2)
        i=0
        self.entryList = []
        for pref in prefs:
            label = gtk.Label("<b>%s</b>"%pref[0])
            label.set_use_markup(True)
            if pref[0] != "status":
                entry = gtk.Entry()
                entry.set_text(pref[1])
                self.entryList.append(entry)
                table.attach(entry,1,2,i,i+1)
            else:
                combobox = gtk.combo_box_new_text()
                combobox.append_text(_("Disable"))
                combobox.append_text(_("Enable"))
                combobox.set_active(int(pref[1]))
                table.attach(combobox,1,2,i,i+1)
                self.entryList.append(combobox)
            table.attach(label,0,1,i,i+1)
            i+=1

        button = gtk.Button(_("Ok"))
        button.connect("clicked", self.on_pluginAcceptSettings_clicked, pluginClass)
        table.attach(button,0,2,i,i+1)
        self.prefwindow.add(table)
        self.prefwindow.show_all()

    def on_pluginAcceptSettings_clicked(self, widget, pluginClass):
        '''
            Duplicate of plugin settings accept handler
        '''
        logging.debug('>>')
        prefs = self.plugins.getPluginConfParams(pluginClass)
        savedOptions = []
        i = 0
        for pref in prefs:
            try:
                savedOptions.append((pref[0],self.entryList[i].get_text()))
            except:
                combobox = self.entryList[i]
                index = combobox.get_active()
                savedOptions.append((pref[0],"%s" %index))
            i+=1
        self.prefwindow.hide()
        self.prefwindow = None
        self.plugins.setPluginConfParams(pluginClass,savedOptions)
        self.init_plugins_tab()
        logging.debug('<<')

    def treeviewImportEvents_header_checkbox(self, column, store):
        '''
            Handler for click on checkbox column
        '''
        logging.debug('--')
        if store is None:
            return
        for item in store:
            if item[1]:
                self.treeviewImportEvents_setCheckboxes(False)
                return
        self.treeviewImportEvents_setCheckboxes(True)

    def on_win_importdata_delete_event(self, widget, window):
        ''' Window closed '''
        logging.debug('--')
        self.close_window()

    def on_notebookMainTabs_switch_page(self, notebook, page, new_page):
        logging.debug('--')
        #self.init_tab(new_page)

    def on_buttonOptionsSave_clicked(self, widget):
        logging.debug('>>')
        self.updateStatusbar(self.statusbarOptions, _("Saving options"))
        self.saveOptions()
        self.updateStatusbar(self.statusbarOptions, _("Options saved"))
        logging.debug('<<')

    def on_buttonOptionsReset_clicked(self, widget):
        logging.debug('>>')
        #GPS Device is default
        self.defaulttab = 0
        #Redisplay tab
        self.init_options_tab()
        self.updateStatusbar(self.statusbarOptions, "")
        logging.debug('<<')

    def on_buttonRemoveSelectedFiles_clicked(self, widget):
        ''' Remove selected files and associated activities from list '''
        logging.debug('>>')
        self.removeSelectedFiles()
        self.updateStatusbar(self.statusbarOptions, "")
        logging.debug('<<')

    def on_buttonFileImport_clicked(self, widget):
        ''' Import selected activities '''
        logging.debug('>>')
        selectedActivities = self.getSelectedActivities()
        selectedCount = len(selectedActivities)
        if selectedCount > 0:
            if selectedCount == 1:
                msgImporting = _("Importing one activity")
            else:
                msgImporting = _("Importing %d activities") % selectedCount
            self.updateStatusbar(self.statusbarImportFile, msgImporting)
            logging.debug(msgImporting)
            while gtk.events_pending(): # This allows the GUI to update
                gtk.main_iteration()    # before completion of this entire action
            importedActivities = self.importSelectedActivities(selectedActivities)
            # Preparing feedback for user
            if importedActivities == 0:
                msgImported = _("No activity has been imported")
            elif importedActivities == 1:
                msgImported = _("Imported one activity")
            elif importedActivities > 1:
                msgImported = _("Imported %d activities") % importedActivities
            discardedActivities = selectedCount - importedActivities
            if discardedActivities > 0:
                if discardedActivities == 1:
                    msgImported += _(" Activity selected was already present in DB")
                else:
                    msgImported += _(" %d selected activities were already present in DB") % discardedActivities
            self.updateStatusbar(self.statusbarImportFile, msgImported)
            logging.debug(msgImported)
        self.buttonFileImport.set_sensitive(0) #Disable import button
        logging.debug('<<')

    def on_buttonSelectFiles_clicked(self, widget):
        logging.debug('>>')
        selectedFiles = fileChooserDialog(title=_("Choose a file (or files) to import activities from"), multiple=True).getFiles()
        while gtk.events_pending(): # This allows the GUI to update
            gtk.main_iteration()    # before completion of this entire action
        if selectedFiles is None or len(selectedFiles) == 0:
            #Nothing selected
            logging.debug("No files selected")
            logging.debug('<<')
            return
        logging.debug("%s files selected" % len(selectedFiles))
        for filename in selectedFiles: #Multiple files
            class_index = len(self.processClasses)
            #Validate file
            self.processClasses.append(self.validateFile(filename))
            if self.processClasses[class_index] is not None:
                filetype = self.processClasses[class_index].getFileType()
                self.updateStatusbar(self.statusbarImportFile, _("Found file of type: %s") % filetype )
                logging.debug("Found file of type: %s" % filetype)
                activitiesSummary = self.processClasses[class_index].getActivitiesSummary()
                activity_count = len(activitiesSummary)
                logging.debug("%s activities in file: %s" % (str(activity_count), filename) )
                #Add file to files treeview
                iter = self.files_store.append()
                self.files_store.set(
                    iter,
                    0, class_index,
                    1, True,
                    2, filename,
                    3, self.processClasses[class_index].getFileType(),
                    4, activity_count
                    )
                #File valid, so enable remove button
                self.buttonRemoveSelectedFiles.set_sensitive(1)
                #Get activities in file
                for activity in activitiesSummary:
                    #Add activity details to TreeView store to display
                    if not activity[1]:
                        #Activity selected, so enable import button
                        self.buttonFileImport.set_sensitive(1)
                        note = ""
                    else:
                        note = _("Found in database")
                    activity_iter = self.activities_store.append()
                    # Status (#1) can be changed by user (via checkbox), we need another field to know if activity is in DB 
                    self.activities_store.set(
                        activity_iter,
                        0, activity[0],
                        1, not activity[1],
                        2, activity[2],
                        3, activity[3],
                        4, activity[4],
                        5, activity[5],
                        6, note,
                        7, class_index,
                        8, activity [1],
                        )
            else: #Selected file not understood by any of the process files
                #Display error
                logging.debug("File %s is of unknown or unsupported file type" % filename)
                msg = _("File %s is of unknown or unsupported file type") % filename
                md = gtk.MessageDialog(self.win_importdata, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, msg)
                md.set_title("Error")
                md.run()
                md.destroy()
                self.updateStatusbar(self.statusbarImportFile, "")
        logging.debug('<<')

    def on_buttonFileClose_clicked(self, widget):
        logging.debug('--')
        self.close_window()

    def on_buttonDeviceClose_clicked(self, widget):
        logging.debug('--')
        self.close_window()

    def on_buttonOptionsClose_clicked(self, widget):
        logging.debug('--')
        self.close_window()

    def on_buttonPluginsClose_clicked(self, widget):
        logging.debug('--')
        self.close_window()

    def on_buttonDeviceToolRescan_clicked(self, widget):
        logging.debug('--')
        self.detect_tools()

    def on_comboboxDevice_changed(self, widget):
        logging.debug('--')
        self.detect_tools()

    def on_filechooserCSVImport_file_set(self, widget):
        logging.debug('--')
        filename = widget.get_filename()
        if not os.path.isfile(filename):
            return
        self.updateStatusbar(self.statusbarCSVImport, _("Got file: ") + filename)
        #Enable buttons
        self.buttonCSVProcess.set_sensitive(True)
        self.buttonCSVImport.set_sensitive(True)

    def on_buttonCSVProcess_clicked(self, widget):
        logging.debug('>>')
        #Get selected file
        self.CSVfilename = self.filechooserCSVImport.get_filename()
        if not os.path.isfile(self.CSVfilename):
            return
        #Determine delimiter
        if self.rbCSVTab.get_active():
            self.delimiter = "\t"
        elif self.rbCSVComma.get_active():
            self.delimiter = ","
        elif self.rbCSVOther.get_active():
            self.delimiter = self.entryCSVOther.get_text()
        else:
            self.delimiter = " "

        #Read as delimited file
        csvfile = open(self.CSVfilename, 'rb')
        #See if file has header row
        self.has_header = csv.Sniffer().has_header(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.DictReader(csvfile, delimiter=self.delimiter)
        #Read file to determine fields (must be a better way of doing this)
        for row in reader:
            pass
        #Build array of column names
        if self.has_header:
            #If the file has a header row, use the actual column names
            columns = reader.fieldnames
        else:
            #Otherwise just label them with numbers
            print len(reader.fieldnames)
            columns = [_("Column %d") % x for x in range(0, len(reader.fieldnames))]

        for column in columns:
            self.cbCSVDate.append_text(column)
            self.cbCSVDistance.append_text(column)
            self.cbCSVDuration.append_text(column)
            self.cbCSVTitle.append_text(column)
            self.cbCSVSport.append_text(column)
            self.cbCSVAvgSpeed.append_text(column)
            self.cbCSVMaxSpeed.append_text(column)
            self.cbCSVCal.append_text(column)
            self.cbCSVAccent.append_text(column)
            self.cbCSVDescent.append_text(column)
            self.cbCSVHR.append_text(column)
            self.cbCSVMaxHR.append_text(column)
            self.cbCSVPace.append_text(column)
            self.cbCSVMaxPace.append_text(column)
            self.cbCSVComments.append_text(column)
        self.cbCSVDate.set_active(0)
        self.cbCSVDistance.set_active(0)
        self.cbCSVDuration.set_active(0)
        self.cbCSVTitle.set_active(0)
        self.cbCSVSport.set_active(0)
        self.cbCSVAvgSpeed.set_active(0)
        self.cbCSVMaxSpeed.set_active(0)
        self.cbCSVCal.set_active(0)
        self.cbCSVAccent.set_active(0)
        self.cbCSVDescent.set_active(0)
        self.cbCSVHR.set_active(0)
        self.cbCSVMaxHR.set_active(0)
        self.cbCSVPace.set_active(0)
        self.cbCSVMaxPace.set_active(0)
        self.cbCSVComments.set_active(0)
        logging.debug('<<')


    def on_buttonCSVImport_clicked(self, widget):
        logging.debug('>>')
        #Determine values
        dateCol = self.cbCSVDate.get_active()
        distanceCol = self.cbCSVDistance.get_active()
        durationCol = self.cbCSVDuration.get_active()
        titleCol = self.cbCSVTitle.get_active()
        sportCol = self.cbCSVSport.get_active()
        avgspeedCol = self.cbCSVAvgSpeed.get_active()
        maxspeedCol = self.cbCSVMaxSpeed.get_active()
        calCol = self.cbCSVCal.get_active()
        accCol = self.cbCSVAccent.get_active()
        desCol = self.cbCSVDescent.get_active()
        hrCol = self.cbCSVHR.get_active()
        maxHRCol = self.cbCSVMaxHR.get_active()
        paceCol = self.cbCSVPace.get_active()
        maxPaceCol = self.cbCSVMaxPace.get_active()
        commentsCol = self.cbCSVComments.get_active()

        if dateCol == 0:
            #Error need to have at least a date
            self.updateStatusbar(self.statusbarCSVImport, _("ERROR: Must define at least a date column"))
            return

        #Import...
        #Get selected file
        if not os.path.isfile(self.CSVfilename):
            return
        #Read as delimited file
        csvfile = open(self.CSVfilename, 'rb')
        reader = csv.reader(csvfile, delimiter=self.delimiter)
        #Process File

        for i, row in enumerate(reader):
            if self.has_header and i==0:
                #Ignore first row
                continue
            if not row:
                continue
            data = {}
            #Determine dates
            _date = getDateTime(row[dateCol-1])
            #year, month, day = date.split("-")
            date = _date[1].strftime("%Y-%m-%d")
            zuluDateTime = _date[0].strftime("%Y-%m-%dT%H:%M:%SZ")
            localDateTime = str(_date[1])
            data['date'] = date
            data['date_time_utc'] = zuluDateTime
            data['date_time_local'] = localDateTime
            if distanceCol:
                try:
                    data['distance'] = locale.atof(row[distanceCol-1])
                except:
                    data['distance'] = 0
            else:
                data['distance'] = 0
            if durationCol:
                #calculate duration in sec...
                try:
                    _duration = row[durationCol-1]
                except:
                    _duration = 0
                if _duration.count(':') == 2:
                    #Have 00:00:00 duration
                    h, m, s = _duration.split(':')
                    try:
                        durationSec = int(h)*3600 + int(m)*60 + int(s)
                    except:
                        logging.debug("Error calculating duration for '%s'" % _duration)
                        durationSec = None
                else:
                    try:
                        durationSec = locale.atoi(_duration)
                    except:
                        #Unknown duration
                        logging.debug("Could not determine duration for '%s'" % _duration)
                        durationSec = None
                if durationSec is not None:
                    data['duration'] = durationSec
                    data['time'] = str(durationSec)
            if titleCol:
                try:
                    data['title'] = row[titleCol-1]
                except:
                    pass
            if self.checkbCSVForceSport.get_active():
                sport_id = self.pytrainer_main.record.getSportId(self.comboCSVForceSport.get_active_text(),add=True)
                data['sport'] = sport_id
            elif sportCol:
                #retrieving sport id (adding sport if it doesn't exist yet)
                sport_id = self.pytrainer_main.record.getSportId(row[sportCol-1],add=True)
                data['sport'] = sport_id
            else:
                self.comboCSVForceSport.set_active(0)
                sport_id = self.pytrainer_main.record.getSportId(self.comboCSVForceSport.get_active_text(),add=True)
                data['sport'] = sport_id

            if avgspeedCol:
                #
                try:
                    data['average'] = locale.atof(row[avgspeedCol-1])
                except:
                    pass
            if maxspeedCol:
                try:
                    data['maxspeed'] = locale.atof(row[maxspeedCol-1])
                except:
                    pass
            if calCol:
                try:
                    data['calories'] = locale.atoi(row[calCol-1])
                except:
                    pass
            if accCol:
                try:
                    data['upositive'] = locale.atof(row[accCol-1])
                except:
                    pass
            if desCol:
                try:
                    data['unegative'] = locale.atof(row[desCol-1])
                except:
                    pass
            if hrCol:
                try:
                    data['beats'] = locale.atof(row[hrCol-1])
                except:
                    pass
            if maxHRCol:
                try:
                    data['maxbeats'] = locale.atof(row[maxHRCol-1])
                except:
                    pass
            if paceCol:
                try:
                    data['pace'] = locale.atof(row[paceCol-1])
                except:
                    pass
            if maxPaceCol:
                try:
                    data['maxpace'] = locale.atof(row[maxPaceCol-1])
                except:
                    pass
            if commentsCol:
                try:
                    data['comments'] = row[commentsCol--1]
                except:
                    pass

            #Insert into DB
            logging.debug("Data", data)
            self.pytrainer_main.ddbb.insert_dict('records', data)
        #Display message....
        self.updateStatusbar(self.statusbarCSVImport, _("Import completed. %d rows processed") % i)
        #Disable import button
        self.buttonCSVImport.set_sensitive(0)
        logging.debug('<<')
