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

from __future__ import division
from SimpleGladeApp import SimpleGladeApp
from windowcalendar import WindowCalendar
from pytrainer.core.equipment import EquipmentService
from pytrainer.gui.equipment import EquipmentUi
from pytrainer.core.sport import Sport
import gtk
import gobject
import logging
import pytrainer
import pytrainer.util.color
from pytrainer.gui.color import ColorConverter
import datetime

class FieldValidator (object):
    """ A class to validate all the input fields that can have errors. """

    FV_HEIGHT = 1
    FV_WEIGHT = 2
    FV_BIRTH_DATE = 3
    FV_MAX_HRATE = 4
    FV_MIN_HRATE = 5
    # Profile equipment 
    FV_LIFE_EXPECT = 6 
    FV_PRIOR_USE = 7
    # Profile sports 
    FV_MET = 8
    FV_EXTRA_WEIGHT = 9
    FV_MAX_PACE = 10

    # Log messages (they are not translated)
    FVLM_HEIGHT = 'Invalid height field entered >>'
    FVLM_WEIGHT = 'Invalid weight field entered >>'
    FVLM_BIRTH_DATE = 'Invalid date of birth field entered >>'
    FVLM_MAX_HRATE = 'Invalid max heart rate field entered >>'
    FVLM_MIN_HRATE = 'Invalid resting hear rate field entered >>'
    FVLM_LIFE_EXPECT = 'Invalid life expectancy field entered >>'
    FVLM_PRIOR_USE = 'Invalid prior usage field entered >>'
    FVLM_MET = 'Invalid M.E.T. field entered >>'
    FVLM_EXTRA_WEIGHT = 'Invalid extra weight field entered >>'
    FVLM_MAX_PACE = 'Invalid maximum pace entered >>'

    def __init__(self):
        # The error messages
        self.FVEM_HEIGHT = _('Error with the height field.')
        self.FVEM_WEIGHT = _('Error with the weight field.')
        self.FVEM_BIRTH_DATE = _('Error with the date of birth field.')
        self.FVEM_MAX_HRATE = _('Error with the maximum heart rate field.')
        self.FVEM_MIN_HRATE = _('Error with the resting heart rate field.')
        self.FVEM_LIFE_EXPECT = _('Error with the life expectancy field.')
        self.FVEM_PRIOR_USE = _('Error with the prior usage field.')
        self.FVEM_MET = _('Error with the M.E.T. field.')
        self.FVEM_EXTRA_WEIGHT = _('Error with the extra weight field.')
        self.FVEM_MAX_PACE = _('Error with the maximum pace field.') 

        # Error messages dictionary
        self.errorMessages = { 
            self.FV_HEIGHT: self.FVEM_HEIGHT,
            self.FV_WEIGHT: self.FVEM_WEIGHT,
            self.FV_BIRTH_DATE: self.FVEM_BIRTH_DATE,
            self.FV_MAX_HRATE: self.FVEM_MAX_HRATE,
            self.FV_MIN_HRATE: self.FVEM_MIN_HRATE,
            self.FV_LIFE_EXPECT: self.FVEM_LIFE_EXPECT,
            self.FV_PRIOR_USE: self.FVEM_PRIOR_USE,
            self.FV_MET: self.FVEM_MET,
            self.FV_EXTRA_WEIGHT: self.FVEM_EXTRA_WEIGHT,
            self.FV_MAX_PACE: self.FVEM_MAX_PACE,
        }

        # Log messages dictionary
        self.logMessages = { 
            self.FV_HEIGHT: self.FVLM_HEIGHT,
            self.FV_WEIGHT: self.FVLM_WEIGHT,
            self.FV_BIRTH_DATE: self.FVLM_BIRTH_DATE,
            self.FV_MAX_HRATE: self.FVLM_MAX_HRATE,
            self.FV_MIN_HRATE: self.FVLM_MIN_HRATE,
            self.FV_LIFE_EXPECT: self.FVLM_LIFE_EXPECT,
            self.FV_PRIOR_USE: self.FVLM_PRIOR_USE,
            self.FV_MET: self.FVLM_MET,
            self.FV_EXTRA_WEIGHT: self.FVLM_EXTRA_WEIGHT,
            self.FV_MAX_PACE: self.FVLM_MAX_PACE,
        }

        # Function dictionary
        self.functions = {
            self.FV_HEIGHT: self.validatePositiveIntegerField,
            self.FV_WEIGHT: self.validatePositiveIntegerField,
            self.FV_BIRTH_DATE: self.validateDate,
            self.FV_MAX_HRATE: self.validatePositiveIntegerField,
            self.FV_MIN_HRATE: self.validatePositiveIntegerField,
            self.FV_LIFE_EXPECT: self.validatePositiveIntegerField,
            self.FV_PRIOR_USE: self.validatePositiveIntegerOrZeroField,
            self.FV_MET: self.validatePositiveIntegerField,
            self.FV_EXTRA_WEIGHT: self.validatePositiveRealField,
            self.FV_MAX_PACE: self.validatePositiveIntegerField,
        }

        # Main profile fields
        self.profileFields = [
            self.FV_HEIGHT,
            self.FV_WEIGHT, 
            self.FV_MAX_HRATE,
            self.FV_MIN_HRATE,
            self.FV_BIRTH_DATE] 

        self.equipmentFields = [
            self.FV_LIFE_EXPECT,
            self.FV_PRIOR_USE,
        ]

        self.sportFields = [
            self.FV_MET,
            self.FV_EXTRA_WEIGHT,
            self.FV_MAX_PACE,
        ]



    def validatePositiveIntegerField (self, field, include0 = False):
        retVal = False
        if field == '':
            retVal = True
        else:
            try:
                a = int (field)
                if (a == 0) and include0:
                    retVal = True
                elif a > 0:
                    retVal = True
            except:
                pass
        return retVal

    def validatePositiveIntegerOrZeroField (self, field):
        return self.validatePositiveIntegerField (field, True)

    def validatePositiveRealField (self, field, include0 = True):
        retVal = False
        if field == '':
            retVal = True
        else:
            try:
                a = float (field)
                if (a == 0.0) and include0:
                    retVal = True
                elif a > 0.0:
                    retVal = True
            except:
                pass
        return retVal


    def validateDate (self, dateStr):
        retVal = False

        if dateStr == '':
            retVal = True
        else:
            try:
                year,month,day = dateStr.split ('-')
                if (len(year) == 4):
                    d = datetime.datetime (int(year), int(month), int (day), \
                            0,0,0)
                    retVal = True
            except:
                pass

        return retVal

    def validateFields (self, fieldDicitionary):
        """ The function receives a dictionary containing pairs FV value and 
            string field. 
            The function returns True if all the fields are ok. 
            In case of error, a message is returned along whit False. """
        retVal = True
        errMsg = ''

        for f in self.profileFields:
            retVal = self.functions [f] (fieldDicitionary[f])
            if not retVal:
                errMsg = self.errorMessages[f]
                retVal = False
                break

        return retVal, errMsg

    def validateSingleFieldAndLog (self, fieldId, fieldStr):
        retVal =  self.functions[fieldId] (fieldStr)
        if not retVal:
            logging.warning (self.logMessages[fieldId] + fieldStr + '<<')
        return retVal

    def validateEquipmentFields (self, fieldDict):
        """ The function receives a dictionary containing pairs FV value and 
            string field related to an equipment form. 
            The function returns True if all the fields are ok. 
            In case of error, a message is returned along whit False. """
        retVal = True
        errMsg = ''

        for f in self.equipmentFields:
            retVal = self.functions [f] (fieldDict[f])
            if not retVal:
                errMsg = self.errorMessages[f]
                retVal = False
                break

        return retVal, errMsg


    def validateSportFields (self, fieldDict):
        """ The function receives a dictionary containing pairs FV value and 
            string field related to a sport form. 
            The function returns True if all the fields are ok. 
            In case of error, a message is returned along whit False. """
        retVal = True
        errMsg = ''

        for f in self.sportFields:
            retVal = self.functions [f] (fieldDict[f])
            if not retVal:
                errMsg = self.errorMessages[f]
                retVal = False
                break

        return retVal, errMsg

class WindowProfile(SimpleGladeApp):
    def __init__(self, sport_service, data_path = None, parent=None, pytrainer_main=None):
        glade_path="glade/profile.glade"
        root = "newprofile"
        domain = None
        self.parent = parent
        self.pytrainer_main = pytrainer_main
        self.data_path = data_path
        SimpleGladeApp.__init__(self, data_path+glade_path, root, domain)
        self.conf_options = parent.profile_options
        self.stored_color = pytrainer.util.color.Color(0)
        self._sport_service = sport_service

    def new(self):
        self.gender_options = {
            0:_("Male"),
            1:_("Female")
            }

        self.ddbb_type = {
            0:"sqlite",
            1:"mysql"
            }
    
        #anhadimos las opciones al combobox gender
        for i in self.gender_options:
            self.prf_gender.insert_text(i,self.gender_options[i])
        
        #hacemos lo propio para el combobox ddbb 
        for i in self.ddbb_type:
            self.prf_ddbb.insert_text(i,self.ddbb_type[i])

        #preparamos la lista sports:
        column_names=[_("Sport"),_("MET"),_("Extra Weight"), _("Maximum Pace"), _("Color")]
        for column_index, column_name in enumerate(column_names):
            if column_index==4:
                renderer = gtk.CellRendererPixbuf()
            else:
                renderer = gtk.CellRendererText()
            column = gtk.TreeViewColumn(column_name, text=column_index)
            column.pack_start(renderer, expand=False)
            if column_index==4:
                column.add_attribute(renderer, 'pixbuf', column_index)
            else:
                column.add_attribute(renderer, 'text', column_index)
            column.set_resizable(True)
            self.sportTreeView.append_column(column)

        #initialise equipment tab:
        equipment_service = EquipmentService(self.pytrainer_main.ddbb)
        equipment_ui = EquipmentUi(self.data_path + "/glade", equipment_service)
        self.equipment_container.add(equipment_ui)            
        
    def present(self):
        self.newprofile.present()
        
    def setValues(self,list_options):
        for i in self.conf_options.keys():
            if not list_options.has_key(i):
                print 'no list options for: ' + i
                continue
            if i == "default_viewer":
                if list_options[i] == "1":
                    logging.debug("Setting defult map viewer to OSM")
                    self.radiobuttonDefaultOSM.set_active(1)
                else:
                    logging.debug("Setting defult map viewer to Google")
                    self.radiobuttonDefaultGMap.set_active(1)
            else:
                try:
                    var = getattr(self,i)
                except AttributeError as e:
                    continue                
                if i == "prf_hrzones_karvonen" or i == "prf_us_system":
                    if list_options[i]=="True":
                        var.set_active(True)
    
                elif i == "prf_gender":
                    for j in self.gender_options:
                        if self.gender_options[j]==list_options[i]:
                            var.set_active(j)
                elif i == "prf_ddbb":
                    for j in self.ddbb_type:
                        if self.ddbb_type[j]==list_options[i]:
                            var.set_active(j)
                            if j==0:
                                self._ddbb_value_deactive()
                            else:
                                self._ddbb_value_active()
                else:
                    var.set_text(list_options[i])
    
    def saveOptions(self):
        list_options = {}
        for i in self.conf_options.keys():
            if i == "default_viewer":
                if self.radiobuttonDefaultOSM.get_active():
                    list_options[i] = "1"
                else:
                    list_options[i] = "0"
            else:
                try:
                    var = getattr(self,i)
                except AttributeError as e:
                    continue
                if i == "prf_hrzones_karvonen" or i == "prf_us_system":
                    if var.get_active():
                        list_options[i] = "True"
                    else:
                        list_options[i] = "False"
                elif i == "prf_gender" or i == "prf_ddbb":
                    list_options[i] = var.get_active_text()
                else:
                    list_options[i] = var.get_text()
        self.parent.setProfile(list_options)
    
    def on_calendar_clicked(self,widget):
        calendardialog = WindowCalendar(self.data_path,self)
        calendardialog.run()

    def setDate(self,date):
        self.prf_age.set_text(date)

    def on_switch_page(self,widget,pointer,frame):
        #print widget, pointer, frame
        if frame==2:
            self.saveOptions()
            sport_list = self._sport_service.get_all_sports()
            store = gtk.ListStore(
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING,
                        gobject.TYPE_STRING,
                        gtk.gdk.Pixbuf,
                        object)
            for sport in sport_list:
                iter = store.append()
                colorPixBuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 25, 15)
                colorPixBuf.fill(sport.color.rgba_val)
                store.set(iter,
                    0, sport.name,
                    1, sport.met,
                    2, sport.weight,
                    3, sport.max_pace,
                    4, colorPixBuf)
            self.sportTreeView.set_model(store)
            self.sportTreeView.set_cursor(0)
            self.sportlist.show()
        elif frame == 5: #Startup Parameters page selected
            self.init_params_tab()
    
    def init_params_tab(self):
        #Show log level
        if self.pytrainer_main.startup_options.log_level == logging.ERROR:
            self.comboboxLogLevel.set_active(0)
        elif self.pytrainer_main.startup_options.log_level == logging.WARNING:
            self.comboboxLogLevel.set_active(1)
        elif self.pytrainer_main.startup_options.log_level == logging.INFO:
            self.comboboxLogLevel.set_active(2)
        elif self.pytrainer_main.startup_options.log_level == logging.DEBUG:
            self.comboboxLogLevel.set_active(3)
        else:
            self.comboboxLogLevel.set_active(0)
            print "Unknown logging level specified"

        #Show if validation requested
        if self.pytrainer_main.startup_options.validate:
            self.checkbuttonValidate.set_active(True)
        else:
            self.checkbuttonValidate.set_active(False)
            
        #Show if new graph activated
        if self.pytrainer_main.startup_options.newgraph:
            self.checkbuttonNewGraph.set_active(True)
        else:
            self.checkbuttonNewGraph.set_active(False)
        
    def on_comboboxLogLevel_changed(self, widget):
        active = self.comboboxLogLevel.get_active()
        if active == 1:
            logging.debug("Setting log level to WARNING")
            self.pytrainer_main.startup_options.log_level = logging.WARNING
        elif active == 2:
            logging.debug("Setting log level to INFO")
            self.pytrainer_main.startup_options.log_level = logging.INFO
        elif active == 3:
            logging.debug("Setting log level to DEBUG")
            self.pytrainer_main.startup_options.log_level = logging.DEBUG
        else:
            logging.debug("Setting log level to ERROR")
            self.pytrainer_main.startup_options.log_level = logging.ERROR
        self.pytrainer_main.set_logging_level(self.pytrainer_main.startup_options.log_level)    
        
    def on_checkbuttonValidate_toggled(self, widget):
        if self.checkbuttonValidate.get_active():
            logging.debug( "Validate activated")
            self.pytrainer_main.startup_options.validate = True
        else:
            logging.debug("Validate deactivated")
            self.pytrainer_main.startup_options.validate = False
            
    def on_checkbuttonNewGraph_toggled(self, widget):
        if self.checkbuttonNewGraph.get_active():
            logging.debug("NewGraph activated")
            self.pytrainer_main.startup_options.newgraph = True
        else:
            logging.debug("NewGraph deactivated")
            self.pytrainer_main.startup_options.newgraph = False       
    
    def on_accept_clicked(self,widget):
        self.saveOptions()
        self.close_window()
    
    def on_cancel_clicked(self,widget):
        self.close_window()

    def close_window(self):
        self.newprofile.hide()
        self.newprofile = None
        self.quit()

    def _ddbb_value_active(self):
        self.prf_ddbbhost_label.set_sensitive(1)
        self.prf_ddbbname_label.set_sensitive(1)
        self.prf_ddbbuser_label.set_sensitive(1)
        self.prf_ddbbpass_label.set_sensitive(1)
        self.prf_ddbbhost.set_sensitive(1)
        self.prf_ddbbname.set_sensitive(1)
        self.prf_ddbbuser.set_sensitive(1)
        self.prf_ddbbpass.set_sensitive(1)
    
    def _ddbb_value_deactive(self):
        self.prf_ddbbhost_label.set_sensitive(0)
        self.prf_ddbbname_label.set_sensitive(0)
        self.prf_ddbbuser_label.set_sensitive(0)
        self.prf_ddbbpass_label.set_sensitive(0)
        self.prf_ddbbhost.set_sensitive(0)
        self.prf_ddbbname.set_sensitive(0)
        self.prf_ddbbuser.set_sensitive(0)
        self.prf_ddbbpass.set_sensitive(0)

    def on_prf_ddbb_changed(self,widget):
        i = self.prf_ddbb.get_active_text()
        if i == "mysql":
            self._ddbb_value_active()
        else:
            self._ddbb_value_deactive()

    def on_addsport_clicked(self,widget):
        self.hidesportsteps()
        self.buttonbox.set_sensitive(0)
        self.addsport.show()

    def on_newsport_accept_clicked(self,widget):
        sport = Sport()
        sport.name = unicode(self.newsportentry.get_text())
        sport.met = self._trim_to_null(self.newmetentry.get_text())
        sport.weight = self.newweightentry.get_text()
        sport.max_pace = self._trim_to_null(self.newmaxpace.get_text())
        sport.color = self.stored_color
        if sport.name.lower() in [s.name.lower() for s in self._sport_service.get_all_sports()]:
            msg = "Sport '%s' already exists" % sport.name
            logging.error(msg)
            md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, _(msg))
            md.set_title(_("Sport Creation Error"))
            md.run()
            md.destroy()
            return
        self._sport_service.store_sport(sport)
        self.parent.actualize_mainsportlist()
        self.on_switch_page(None,None,2)
        self.hidesportsteps()
        self.buttonbox.set_sensitive(1)
        self.sportlist.show()

    def on_delsport_clicked(self,widget):
        selected,iter = self.sportTreeView.get_selection().get_selected()
        if iter:
            self.buttonbox.set_sensitive(0)
            sport = selected.get_value(iter,0)
            self.sportnamedel.set_text(sport)
            self.hidesportsteps()
            self.deletesport.show()

    def on_deletesport_clicked(self,widget):
        sport_name = self.sportnamedel.get_text()
        sport = self._sport_service.get_sport_by_name(sport_name)
        self._sport_service.remove_sport(sport)
        self.parent.actualize_mainsportlist()
        self.on_switch_page(None,None,2)
        self.hidesportsteps()
        self.buttonbox.set_sensitive(1)
        self.sportlist.show()
    
    def on_editsport_clicked(self,widget):
        selected,iter = self.sportTreeView.get_selection().get_selected()
        if iter:
            self.buttonbox.set_sensitive(0)
            sport_desc = selected.get_value(iter,0)
            sport = self._sport_service.get_sport_by_name(sport_desc)
            self.editsportentry.set_text(sport.name)
            self.sportnameedit.set_text(sport.name)
            self.editweightentry.set_text(str(sport.weight))
            met_str = "" if sport.met is None else str(sport.met)
            self.editmetentry.set_text(met_str)
            max_pace_str = "" if sport.max_pace is None else str(sport.max_pace)
            self.editmaxpace.set_text(max_pace_str)
            colorPixBuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 250, 20)
            colorPixBuf.fill(sport.color.rgba_val)
            self.editcolor.set_from_pixbuf(colorPixBuf)
            self.hidesportsteps()
            self.editsport.show()
            
    def on_editcolor_clicked(self, widget):
        selected,iter = self.sportTreeView.get_selection().get_selected()
        if iter:
            sport_desc = selected.get_value(iter,0)
            sport = self._sport_service.get_sport_by_name(sport_desc)
            colorseldlg = gtk.ColorSelectionDialog("test")
            colorseldlg.colorsel.set_has_palette(True)
            colorseldlg.colorsel.set_current_color(ColorConverter().convert_to_gdk_color(sport.color))
            colorseldlg.run()
            gdk_color = colorseldlg.colorsel.get_current_color()
            self.stored_color = ColorConverter().convert_to_color(gdk_color)
            colorPixBuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 250, 20)
            colorPixBuf.fill(self.stored_color.rgba_val)
            self.newcolor.set_from_pixbuf(colorPixBuf)
            self.editcolor.set_from_pixbuf(colorPixBuf)
            
            colorseldlg.hide()
            
    def on_sporttreeview_row_activated(self, widget, path, column):
        self.on_editsport_clicked(None)
    
    def on_editsport_accept_clicked(self,widget):
        oldnamesport = self.sportnameedit.get_text()
        sport = self._sport_service.get_sport_by_name(oldnamesport)
        sport.name = unicode(self.editsportentry.get_text())
        sport.weight = self.editweightentry.get_text()
        sport.met = self._trim_to_null(self.editmetentry.get_text())
        sport.max_pace = self._trim_to_null(self.editmaxpace.get_text())
        sport.color = self.stored_color
        self._sport_service.store_sport(sport)
        self.parent.actualize_mainsportlist()
        self.on_switch_page(None,None,2)
        self.hidesportsteps()
        self.buttonbox.set_sensitive(1)
        self.sportlist.show()
        
    def _trim_to_null(self, string):
        trimmed = string.strip()
        return None if trimmed == "" else trimmed
        
    def on_sportcancel_clicked(self,widget):
        self.hidesportsteps()
        self.buttonbox.set_sensitive(1)
        self.sportlist.show()

    def on_calculatemaxhr_clicked(self,widget=None):
        today = "%s"%datetime.date.today()
        year1,month1,day1 = today.split("-")
        year2,month2,day2 = self.prf_age.get_text().split("-")
        diff = datetime.datetime(int(year1), int(month1), int(day1),0,0,0) - datetime.datetime(int(year2), int(month2), int(day2),0,0,0)
        self.prf_maxhr.set_text("%d" %(220-int(diff.days/365)))

    def hidesportsteps(self):
        self.sportlist.hide()
        self.addsport.hide()
        self.deletesport.hide()
        self.editsport.hide()   

    def validateFields (self, originField):
        # A dictionary containing all the fields to validate
        fieldDict = {}
        fieldDict [FieldValidator.FV_HEIGHT] = self.prf_height.get_text()
        fieldDict [FieldValidator.FV_WEIGHT] = self.prf_weight.get_text()
        fieldDict [FieldValidator.FV_BIRTH_DATE] = self.prf_age.get_text()
        fieldDict [FieldValidator.FV_MAX_HRATE] = self.prf_maxhr.get_text()
        fieldDict [FieldValidator.FV_MIN_HRATE] = self.prf_minhr.get_text()

        F = FieldValidator ()

        F.validateSingleFieldAndLog (originField, fieldDict[originField])

        retVal, errMsg = F.validateFields (fieldDict)
        self.button3.set_sensitive (retVal)
        if errMsg == '':
            msg = ''
        else:
            msg = '<span weight="bold"' + " fgcolor='#ff0000'>" +\
                  str(errMsg) + '</span>'
        self.label12.set_markup (msg)

    def on_prf_height_focus_out_event(self, widget, data):
        self.validateFields (FieldValidator.FV_HEIGHT)

    def on_prf_weight_focus_out_event (self, widget, data):
        self.validateFields (FieldValidator.FV_WEIGHT)

    def on_prf_age_focus_out_event (self, widget, data):
        self.validateFields (FieldValidator.FV_BIRTH_DATE)

    def on_prf_maxhr_focus_out_event (self, widget, data):
        self.validateFields (FieldValidator.FV_MAX_HRATE)

    def on_prf_minhr_focus_out_event (self, widget, data):
        self.validateFields (FieldValidator.FV_MIN_HRATE)

