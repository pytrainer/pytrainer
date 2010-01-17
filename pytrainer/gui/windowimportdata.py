# -*- coding: iso-8859-1 -*-

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

from SimpleGladeApp import SimpleGladeApp
import gtk
import gobject
import os, glob, sys
import StringIO
import logging
from lxml import etree

class WindowImportdata(SimpleGladeApp):
	def __init__(self, data_path = None, parent=None, config=None):
		self.data_path = data_path
		self.glade_path=data_path+"glade/importdata.glade"
		self.root = "win_importdata"
		self.domain = None
		self.parent = parent
		self.configuration = config
		self.store = None
		self.processClass = None
		#SimpleGladeApp.__init__(self, data_path+glade_path, root, domain)

	def run(self):
		SimpleGladeApp.__init__(self, self.glade_path, self.root, self.domain)
		
	def new(self):
		self.defaulttab = self.configuration.getValue("pytraining","import_default_tab")
		if self.defaulttab == "":
			self.defaulttab = 0
		else:
			self.defaulttab = int(self.defaulttab)
		self.notebookMainTabs.set_current_page(self.defaulttab)
		self.init_tab(self.defaulttab)

	def init_tab(self, page):
		if page == 0:
			#'Import from GPS Device' tab
			self.init_gpsdevice_tab()
		elif page == 1:
			#'Import from File' tab
			self.init_file_tab()
		elif page ==2:
			#'Options' tab
			self.init_options_tab()
		else:
			#unknown tab
			pass

	def updateStatusbar(self, statusbar, text, context_id = None):
		if context_id is None:
			context_id = statusbar.get_context_id(text)
		statusbar.push(context_id, text)
		return context_id

	def init_gpsdevice_tab(self):

		return

	def init_file_tab(self):
		self.filechooserbuttonSelectFile.unselect_all() 
		self.updateStatusbar(self.statusbarImportFile, _("No file selected") )
		self.processClass = None
		if self.store is None:
			self.store = self.build_tree_view()
		else:
			self.store.clear()
		self.buttonClearFile.set_sensitive(0)
		self.buttonFileImport.set_sensitive(0)
		return

	def init_options_tab(self):
		#Set correct radiobutton based on saved preference
		if self.defaulttab == 1:
			self.radiobuttonFile.set_active(1)
		else:
			self.radiobuttonTabGPSDevice.set_active(1)
		return
	
	def detect_tools(self):
		"""
			Iterate through all tool files from import directory
			Each file contains information on a particular tool 
			and knows how to determine if the tool is present on the system 
			and what configuration options are needed for the tool
	
			Currently displays the tool info and config grayed out if tool is not present
		"""
		logging.debug('>>')
		self.updateStatusbar(self.statusbarDevice, "Checking for tools")
		#Remove all components in vbox - in case of re-detection
		for child in self.vboxImportTools.get_children():
			print "removing ", child
			self.vboxImportTools.remove(child)
		#Get import tool_* files
		fileList = glob.glob(self.data_path+"import/tool_*.py")
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

	def validateFile(self, import_filename):
		"""
			Iterate through all supported types of file by reading processing files from import directory
			Each processing file understands one type of file

			If a processing file is found that recognises the selected file:
				 returns the instantiated class
			otherwise:
				 returns None
		"""
		logging.debug('>>')
		self.updateStatusbar(self.statusbarImportFile, "Checking file type for: " + import_filename)
		#Get import files_* files
		fileList = glob.glob(self.data_path+"import/file_*.py")
		for processingFile in fileList:
			directory, filename = os.path.split(processingFile)
			filename = filename.rstrip('.py') 
			classname = filename.lstrip('file_')
			#Import module
			sys.path.insert(0, self.data_path+"import")
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

		
		self.updateStatusbar(self.statusbarImportFile, "Unknown file type")
		logging.debug('<<')
		return None

	def build_tree_view(self):
		store = gtk.ListStore(gobject.TYPE_STRING,
								gobject.TYPE_BOOLEAN, 
								gobject.TYPE_STRING, 
								gobject.TYPE_STRING, 
								gobject.TYPE_STRING, 
								gobject.TYPE_STRING, 								 
								gobject.TYPE_STRING )
		column_names=["id", _(""),_("Start Time"), _("Distance"),_("Duration"),_("Sport"), _("Notes")]
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
			if column_name == "id":
				column.set_visible(False)
			column.set_resizable(True)
			self.treeviewImportEvents.append_column(column)
		self.treeviewImportEvents.set_headers_clickable(True)
		self.treeviewImportEvents.set_model(store)
		return store

	def treeviewImportEvents_toggled_checkbox( self, cell, path, store ):
		"""
			Sets the state of the checkbox to true or false.
		"""
		store[path][1] = not store[path][1]
		self.buttonFileImport.set_sensitive(0)
		for item in store:
			if item[1]:
				#Only enable import button if at least one activity is selected
				self.buttonFileImport.set_sensitive(1)
		return	

	def treeviewImportEvents_setCheckboxes(self, state):
		"""
			Sets or unsets all checkboxes
		"""
		if self.store is None or len(self.store) == 0:
			return
		for item in self.store:
			item[1] = state
		if state:
			self.buttonFileImport.set_sensitive(1)
		else:
			self.buttonFileImport.set_sensitive(0)			

	def saveOptions(self):
		"""
			Save options selected in options tab
		"""
		#Default tab option
		if self.radiobuttonTabGPSDevice.get_active():
			self.defaulttab = "0"
		elif self.radiobuttonFile.get_active():
			self.defaulttab = "1"
		self.configuration.setValue("pytraining","import_default_tab",self.defaulttab)	
		#option

	def getSelectedActivities(self):
		"""
			Function to determine which activities are selected
			
			Returns array of the ids of the selected activities
		"""
		selectedActivities = []
		if self.store is None:
			return None
		for item in self.store:
			if item[1] is True: #Checkbox is True
				logging.debug("Added activity id:%s to selected list" % item[0])
				selectedActivities.append(item[0])
		logging.debug( "Found %d selected activities to import" % len(selectedActivities) )
		return selectedActivities
		
	def importSelectedActivities(self, selectedActivities):
		"""
			Function to import selected activities
		"""
		if selectedActivities is None or len(selectedActivities) == 0:
			return
		for activityID in selectedActivities:
			logging.debug( "Importing activity %s" % activityID)
			sport, gpxFile = self.processClass.getGPXFile(activityID)
			#process returned GPX files	
			if os.path.isfile(gpxFile):
				logging.info('File exists. Size: %d. Sport: %s' % (os.path.getsize(gpxFile), sport))
				#TODO trigger newentry screen to allow user to edit data
				self.parent.parent.record.importFromGPX(gpxFile, sport)
				#Deselect imported activity and change note
				self.updateActivity(activityID, status=False, notes="Imported into database")
 			else:
 				logging.error('File %s not valid' % gpxFile)


	def updateActivity(self, activityID, status = None, notes = None):
		path = 0
		for item in self.store:
			if item[0] == activityID:
				if status is not None:
					self.store[path][1] = status
				if notes is not None:
					self.store[path][6] = notes
			path +=1

	def close_window(self):
		self.win_importdata.hide()
		self.win_importdata.destroy()

	############################
	## Window signal handlers ##
	############################

	def treeviewImportEvents_header_checkbox(self, column, store):
		"""
			Handler for click on checkbox column
		"""
		if store is None:
			return
		for item in store:
			if item[1]:
				self.treeviewImportEvents_setCheckboxes(False)
				return
		self.treeviewImportEvents_setCheckboxes(True)

	def on_win_importdata_delete_event(self, widget, window):
		""" Windows closed """
		self.close_window()
		
	def on_notebookMainTabs_switch_page(self, notebook, page, new_page):
		self.init_tab(new_page)

	def on_filechooserbuttonSelectFile_file_set(self, widget):
		self.buttonClearFile.set_sensitive(1) #Enable clear button
		self.buttonFileImport.set_sensitive(0) #Disable import button
		self.updateStatusbar(self.statusbarImportFile, "" ) #Clear status bar
		#Clear store
		if self.store is not None:
			self.store.clear()
		#Validate file
		self.processClass = self.validateFile(self.filechooserbuttonSelectFile.get_filename())
		if self.processClass is not None:
			self.updateStatusbar(self.statusbarImportFile, _("Found file of type: %s") % self.processClass.getFileType() )
			#Get activities in file
			activitiesSummary = self.processClass.getActivitiesSummary()			
			for activity in activitiesSummary:
				if not activity[1]:
					#Activity selected, so enable import button
					self.buttonFileImport.set_sensitive(1)
					note = ""
				else:
					note = _("Found in database")
				#Add activity details to TreeView store to display
				iter = self.store.append()
				self.store.set(
					iter,
					0, activity[0],
					1, not activity[1],
					2, activity[2],
					3, activity[3],
					4, activity[4],
					5, activity[5],
					6, note,
					)
		else:
			#Selected file not understood by any of the process files
			self.updateStatusbar(self.statusbarImportFile, _("Unknown file type") )
			#Display error
			msg = _("File selected is of unknown or unsupported file type")
			md = gtk.MessageDialog(self.win_importdata, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, msg)
			md.set_title("Error")
			md.run()
			md.destroy()

	def on_buttonClearFile_clicked(self, widget):	
		self.init_tab(1)

	def on_buttonOptionsSave_clicked(self, widget):
		self.updateStatusbar(self.statusbarOptions, "Saving options")
		self.saveOptions()
		self.updateStatusbar(self.statusbarOptions, "Options saved")

	def on_buttonOptionsReset_clicked(self, widget):
		#GPS Device is default
		self.defaulttab = 0
		#Redisplay tab
		self.init_options_tab()
		self.updateStatusbar(self.statusbarOptions, "")

	def on_buttonFileImport_clicked(self, widget):
		#Import selected activities
		selectedActivities = self.getSelectedActivities()
		selectedCount = len(selectedActivities)
		if selectedCount > 0:
			if selectedCount == 1:
				msgImporting = _("Importing one activity")
				msgImported = _("Imported one activity")
			else:
				msgImporting = _("Importing %d activities" % selectedCount)
				msgImported = _("Imported %d activities" % selectedCount)
			self.updateStatusbar(self.statusbarImportFile, msgImporting)
			while gtk.events_pending():	# This allows the GUI to update 
				gtk.main_iteration()	# before completion of this entire action
			self.importSelectedActivities(selectedActivities)
			self.updateStatusbar(self.statusbarImportFile, msgImported)
			#Display informational dialog box
			md = gtk.MessageDialog(self.win_importdata, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, msgImported)
			md.set_title(_("Import Success"))
			md.run()
			md.destroy()
		self.buttonFileImport.set_sensitive(0) #Disable import button

	def on_buttonFileClose_clicked(self, widget):
		self.close_window()

	def on_buttonDeviceClose_clicked(self, widget):
		self.close_window()

	def on_buttonOptionsClose_clicked(self, widget):
		self.close_window()

	def on_buttonDeviceToolRescan_clicked(self, widget):
		self.detect_tools()

	def on_comboboxDevice_changed(self, widget):
		self.detect_tools()
